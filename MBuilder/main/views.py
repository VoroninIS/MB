from django.shortcuts import render
from .forms import SchemGenerateForm
from django.http import HttpResponse
from django.core.files.base import ContentFile

import os
import cv2
import numpy as np
import torch
import open3d as o3d
import uuid
import mcschematic
import tempfile
import logging
from django.core import signals
from django.conf import settings
from functools import lru_cache
from django.http import FileResponse
from django.http import JsonResponse
from django.core.signals import request_finished
from shap_e.diffusion.sample import sample_latents  # type: ignore
from shap_e.diffusion.gaussian_diffusion import diffusion_from_config  # type: ignore
from shap_e.models.download import load_model, load_config  # type: ignore
from shap_e.util.notebooks import create_pan_cameras, decode_latent_images, gif_widget  # type: ignore
from shap_e.util.notebooks import decode_latent_mesh  # type: ignore


def index(request):
    form = SchemGenerateForm()
    data = {"form": form}
    return render(request, "main/index.html", data)


def schem_generation(request):
    if request.method == "GET":
        form = SchemGenerateForm(request.GET)
        if form.is_valid():
            prompt = form.cleaned_data["prompt"]
            filename = prompt.replace(" ", "_")
            file_path = settings.MEDIA_ROOT

            schem = generate(prompt)
            schem.save(
                settings.MEDIA_ROOT,
                filename,
                mcschematic.Version.JE_1_20_1,
            )

            full_name = file_path + "/" + filename + ".schem"
            file_handle = open(full_name, "rb")
            response = DeleteFileAfter(
                file_handle,
                delete_file=full_name,
                content_type="application/octet-stream",
            )

            response["Content-Disposition"] = f'attachment; filename="{filename}.schem"'
            return response
        else:
            # Возвращаем ошибки валидации в JSON
            errors = form.errors.get_json_data()
            return JsonResponse({"errors": errors}, status=400, safe=False)
    return JsonResponse({"error": "Invalid request method"}, status=405)


class DeleteFileAfter(FileResponse):
    def __init__(
        self, *args, delete_file, as_attachment=False, filename=None, **kwargs
    ):
        super().__init__(
            *args, as_attachment=as_attachment, filename=filename, **kwargs
        )
        self.delete_file = delete_file

    def close(self):
        super(FileResponse, self).close()
        os.remove(self.delete_file)


def generate(prompt):
    schem = mcschematic.MCSchematic()

    rdm = uuid.uuid1()
    batch_size = 8
    guidance_scale = 5.0

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    xm = load_model("transmitter", device=device)
    model = load_model("text300M", device=device)
    diffusion = diffusion_from_config(load_config("diffusion"))

    latents = sample_latents(
        batch_size=batch_size,
        model=model,
        diffusion=diffusion,
        guidance_scale=guidance_scale,
        model_kwargs=dict(texts=[prompt] * batch_size),
        progress=True,
        clip_denoised=True,
        use_fp16=True,
        use_karras=True,
        karras_steps=32,
        sigma_min=1e-5,
        sigma_max=160,
        s_churn=0,
    )

    for i, latent in enumerate(latents):
        with open(f"out_{rdm}.ply", "wb") as f:
            decode_latent_mesh(xm, latent).tri_mesh().write_ply(f)
            if i == 3:
                break

    pcd = o3d.io.read_point_cloud(f"out_{rdm}.ply")
    pcd.scale(
        1 / np.max(pcd.get_max_bound() - pcd.get_min_bound()), center=pcd.get_center()
    )
    voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size=0.01)
    voxels = voxel_grid.get_voxels()

    schem = mcschematic.MCSchematic()

    for i in range(len(voxels)):
        colorr = voxels[i].color
        index = voxels[i].grid_index
        # print(index)
        block = close_color(colorr[0], colorr[1], colorr[2])
        # rotation when sqve the file
        schem.setBlock((index[0], index[2], index[1]), "minecraft:" + block)

    return schem


def about(request):
    return render(request, "main/about.html")


def faq(request):
    return render(request, "main/faq.html")


def price(request):
    return render(request, "main/price.html")


def support(request):
    return render(request, "main/support.html")


def cookies(request):
    return render(request, "main/cookies.html")


def terms(request):
    return render(request, "main/terms.html")


def privacy(request):
    return render(request, "main/privacy.html")


@lru_cache(maxsize=512)
def close_color(r, g, b):
    block_dict = {
        "purple_wool": (118, 40, 170),
        "pink_terracotta": (235, 154, 181),
        "stripped_acacia_log": (175, 92, 59),
        "soul_torch": (8, 8, 6),
        "chiseled_deepslate": (57, 57, 57),
        "diamond_block": (103, 241, 230),
        "light_gray_terracotta": (145, 175, 176),
        "chiseled_bookshelf_occupied": (99, 80, 69),
        "raw_iron_block": (158, 129, 100),
        "yellow_terracotta": (234, 191, 79),
        "lantern": (44, 40, 35),
        "redstone_dust_dot": (36, 36, 36),
        "white_stained_glass": (255, 255, 255),
        "iron_block": (222, 222, 222),
        "cherry_log": (185, 141, 137),
        "gold_block": (249, 213, 63),
        "orange_wool": (238, 116, 18),
        "purple_stained_glass_pane": (238, 230, 244),
        "orange_stained_glass_pane": (249, 238, 229),
        "orange_concrete": (225, 104, 3),
        "light_gray_stained_glass": (153, 153, 153),
        "netherrack": (96, 38, 38),
        "stonecutter": (123, 122, 123),
        "brown_stained_glass_pane": (235, 232, 229),
        "blue_concrete": (48, 50, 149),
        "pointed_dripstone_up_middle": (93, 74, 64),
        "chiseled_quartz_block": (234, 228, 220),
        "red_concrete": (169, 53, 50),
        "cobbled_deepslate": (76, 76, 80),
        "yellow_stained_glass": (229, 229, 51),
        "purple_stained_glass": (127, 63, 178),
        "gray_terracotta": (81, 88, 91),
        "deepslate": (78, 78, 81),
        "glowstone": (182, 142, 91),
        "diorite": (188, 188, 189),
        "cyan_terracotta": (49, 118, 125),
        "dark_oak_log": (65, 44, 21),
        "raw_copper_block": (158, 106, 79),
        "brown_terracotta": (113, 102, 82),
        "jack_o_lantern": (217, 157, 56),
        "light_blue_concrete": (74, 181, 213),
        "polished_andesite": (130, 132, 132),
        "black_concrete": (25, 27, 32),
        "torchflower_crop_stage0": (2, 8, 5),
        "acacia_log": (102, 95, 85),
        "stone_bricks": (123, 123, 123),
        "deepslate_copper_ore": (90, 91, 87),
        "magenta_stained_glass": (178, 76, 216),
        "bell": (71, 64, 24),
        "dark_oak_planks": (69, 44, 21),
        "blackstone": (41, 35, 41),
        "chain_command_block": (139, 170, 156),
        "pointed_dripstone_down_tip_merge": (41, 33, 28),
        "redstone_dust_line1": (38, 38, 38),
        "andesite": (135, 135, 136),
        "pink_concrete": (231, 151, 181),
        "magenta_terracotta": (206, 92, 193),
        "polished_blackstone_bricks": (48, 42, 49),
        "spruce_log": (57, 36, 16),
        "stripped_mangrove_log": (109, 43, 43),
        "pointed_dripstone_down_frustum": (78, 61, 54),
        "sandstone": (217, 205, 159),
        "red_wool": (159, 38, 34),
        "red_nether_bricks": (70, 7, 9),
        "weathered_copper": (107, 153, 108),
        "black_terracotta": (37, 22, 16),
        "chiseled_stone_bricks": (123, 122, 123),
        "deepslate_bricks": (71, 71, 72),
        "pointed_dripstone_down_base": (112, 89, 77),
        "white_stained_glass_pane": (253, 253, 253),
        "prismarine": (100, 159, 153),
        "cobblestone": (126, 126, 126),
        "purple_concrete": (107, 34, 162),
        "quartz_bricks": (235, 229, 222),
        "torchflower_crop_stage1": (19, 25, 17),
        "gray_wool": (62, 67, 70),
        "nether_bricks": (45, 22, 27),
        "soul_sand": (81, 62, 50),
        "stonecutter_saw": (81, 81, 81),
        "black_wool": (20, 21, 25),
        "cracked_nether_bricks": (42, 21, 25),
        "bricks": (150, 90, 74),
        "sea_lantern": (182, 208, 198),
        "mangrove_planks": (119, 55, 50),
        "black_stained_glass_pane": (226, 226, 226),
        "copper_block": (193, 108, 80),
        "quartz_block": (236, 230, 223),
        "orange_terracotta": (160, 83, 37),
        "iron_bars": (65, 66, 65),
        "white_terracotta": (193, 219, 208),
        "light_gray_concrete": (155, 155, 148),
        "purple_terracotta": (106, 43, 150),
        "deepslate_coal_ore": (71, 71, 72),
        "stripped_birch_log": (198, 176, 118),
        "reinforced_deepslate": (80, 82, 77),
        "bookshelf": (100, 83, 51),
        "blue_wool": (52, 56, 156),
        "stripped_jungle_log": (174, 134, 87),
        "jungle_log": (85, 67, 24),
        "red_stained_glass": (153, 50, 50),
        "calcite": (222, 223, 219),
        "green_stained_glass": (102, 127, 51),
        "stripped_oak_log": (160, 130, 77),
        "grindstone_round": (209, 209, 209),
        "green_terracotta": (76, 83, 42),
        "pointed_dripstone_down_middle": (93, 74, 64),
        "scaffolding": (104, 92, 41),
        "obsidian": (13, 9, 22),
        "dark_prismarine": (54, 96, 80),
        "pink_stained_glass_pane": (252, 238, 242),
        "spruce_planks": (118, 87, 50),
        "red_sandstone": (188, 101, 30),
        "flower_pot": (23, 13, 10),
        "cracked_polished_blackstone_bricks": (45, 39, 45),
        "bamboo_planks": (200, 178, 81),
        "light_blue_stained_glass_pane": (235, 241, 249),
        "mangrove_log": (102, 48, 42),
        "gray_concrete": (58, 61, 66),
        "emerald_block": (42, 210, 93),
        "dripstone_block": (133, 106, 91),
        "polished_diorite": (196, 196, 197),
        "white_concrete": (226, 227, 228),
        "magenta_concrete": (194, 85, 185),
        "smooth_stone": (162, 162, 162),
        "exposed_copper": (161, 124, 101),
        "smooth_stone_slab": (165, 165, 165),
        "end_rod": (48, 45, 42),
        "smooth_basalt": (72, 72, 78),
        "torch": (10, 8, 4),
        "lodestone": (120, 120, 122),
        "stripped_spruce_log": (106, 80, 45),
        "chiseled_bookshelf": (175, 142, 86),
        "brown_wool": (111, 70, 39),
        "acacia_planks": (170, 91, 50),
        "light_blue_terracotta": (114, 109, 138),
        "cyan_concrete": (36, 148, 157),
        "deepslate_redstone_ore": (100, 71, 73),
        "green_concrete": (77, 96, 37),
        "mossy_stone_bricks": (116, 122, 106),
        "blue_stained_glass_pane": (229, 232, 244),
        "gray_stained_glass_pane": (232, 232, 232),
        "chiseled_polished_blackstone": (53, 48, 57),
        "lime_terracotta": (104, 118, 51),
        "yellow_wool": (245, 194, 37),
        "mud_bricks": (142, 107, 80),
        "green_wool": (84, 108, 27),
        "deepslate_tiles": (55, 55, 55),
        "blue_terracotta": (46, 57, 127),
        "redstone_lamp_on": (187, 139, 85),
        "brown_concrete": (100, 62, 33),
        "oak_log": (152, 122, 73),
        "redstone_torch_off": (7, 5, 3),
        "pointed_dripstone_up_tip_merge": (41, 33, 28),
        "prismarine_bricks": (98, 173, 160),
        "jungle_planks": (165, 119, 83),
        "chain": (9, 10, 14),
        "cut_copper": (193, 109, 82),
        "light_blue_stained_glass": (102, 153, 216),
        "cut_red_sandstone": (190, 102, 32),
        "birch_log": (226, 225, 221),
        "gilded_blackstone": (58, 43, 36),
        "pointed_dripstone_up_frustum": (78, 61, 54),
        "oxidized_cut_copper": (81, 156, 126),
        "lime_stained_glass_pane": (238, 247, 226),
        "polished_blackstone": (51, 47, 55),
        "glass": (23, 28, 28),
        "redstone_dust_line0": (32, 32, 32),
        "cracked_stone_bricks": (120, 120, 120),
        "polished_granite": (155, 106, 88),
        "redstone_ore": (138, 110, 110),
        "chiseled_nether_bricks": (48, 24, 28),
        "soul_lantern": (31, 43, 49),
        "weathered_cut_copper": (111, 147, 107),
        "grindstone_pivot": (17, 10, 4),
        "yellow_concrete": (233, 199, 53),
        "blue_stained_glass": (50, 75, 178),
        "magenta_stained_glass_pane": (244, 232, 249),
        "deepslate_emerald_ore": (74, 97, 81),
        "yellow_stained_glass_pane": (250, 250, 229),
        "red_terracotta": (182, 58, 52),
        "cyan_wool": (21, 136, 144),
        "lime_stained_glass": (127, 204, 25),
        "cyan_stained_glass": (76, 127, 153),
        "green_stained_glass_pane": (235, 238, 229),
        "orange_stained_glass": (216, 127, 51),
        "chain_command_block_back": (139, 167, 154),
        "pink_wool": (232, 139, 170),
        "oxidized_copper": (83, 166, 136),
        "end_stone": (219, 223, 158),
        "cracked_deepslate_tiles": (54, 54, 54),
        "pink_stained_glass": (242, 127, 165),
        "light_gray_wool": (140, 140, 133),
        "stripped_dark_oak_log": (74, 57, 36),
        "black_stained_glass": (25, 25, 25),
        "stripped_cherry_log": (215, 145, 149),
        "end_stone_bricks": (220, 226, 162),
        "crying_obsidian": (26, 9, 50),
        "mossy_cobblestone": (109, 118, 93),
        "lime_concrete": (125, 189, 42),
        "oak_planks": (167, 136, 82),
        "raw_gold_block": (221, 169, 45),
        "cyan_stained_glass_pane": (232, 238, 241),
        "pointed_dripstone_up_tip": (21, 17, 14),
        "chiseled_sandstone": (216, 204, 157),
        "chain_command_block_conditional": (138, 171, 156),
        "birch_planks": (196, 178, 122),
        "redstone_torch": (15, 9, 5),
        "terracotta": (151, 93, 67),
        "tuff": (107, 108, 102),
        "gray_stained_glass": (76, 76, 76),
        "cracked_deepslate_bricks": (66, 66, 67),
        "exposed_cut_copper": (156, 122, 100),
        "stone": (124, 124, 124),
        "grindstone": (185, 185, 185),
        "light_blue_wool": (56, 170, 213),
        "lime_wool": (111, 183, 25),
        "magenta_wool": (186, 67, 176),
        "blue_ice": (115, 167, 252),
        "pointed_dripstone_up_base": (112, 89, 77),
        "deepslate_iron_ore": (98, 92, 89),
        "deepslate_diamond_ore": (79, 100, 101),
        "cut_sandstone": (218, 207, 161),
        "pointed_dripstone_down_tip": (21, 17, 14),
        "chiseled_red_sandstone": (184, 98, 28),
        "ladder": (75, 58, 33),
        "glass_pane": (21, 26, 27),
        "chiseled_bookshelf_empty": (76, 58, 33),
        "deepslate_gold_ore": (112, 100, 74),
        "red_stained_glass_pane": (241, 229, 229),
        "soul_soil": (74, 56, 45),
        "redstone_lamp": (118, 69, 37),
        "granite": (150, 102, 85),
        "tinted_glass": (42, 38, 43),
        "cherry_planks": (228, 182, 176),
        "white_wool": (230, 232, 233),
        "deepslate_lapis_ore": (70, 83, 112),
        "light_gray_stained_glass_pane": (241, 241, 241),
        "brown_stained_glass": (102, 76, 51),
        "packed_ice": (141, 180, 250),
        "torchflower": (35, 36, 25),
        "polished_deepslate": (72, 73, 74),
        "redstone_block": (167, 24, 4),
    }
    target_color = np.array([r * 255, g * 255, b * 255])
    min_dist = float("inf")
    closest_block = None
    for block_name, avg_color in block_dict.items():
        dist = np.linalg.norm(target_color - np.array(avg_color))
        if dist < min_dist:
            min_dist = dist
            closest_block = block_name
    return closest_block
