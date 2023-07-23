
from .. import OptInfo, DownloadInfo, RepositoryInfo
from ._path import EXTENSION_DIRECTORY


EXTENSION_LIST = [

    OptInfo(
        name="WebUI images browser",
        default=True,
        description="",
        repos=(
            RepositoryInfo(
                "https://github.com/AlUlkesh/stable-diffusion-webui-images-browser.git",
                EXTENSION_DIRECTORY + "stable-diffusion-webui-images-browser"),
        )
    ),

    OptInfo(
        name="Canvas zoom",
        default=True,
        description="",
        repos=(
            RepositoryInfo(
                "https://github.com/richrobber2/canvas-zoom.git",
                EXTENSION_DIRECTORY + "canvas-zoom"),
        )
    ),

    OptInfo(
        name="Aspect ratio helper",
        default=True,
        description="",
        repos=(
            RepositoryInfo(
                "https://github.com/thomasasfk/sd-webui-aspect-ratio-helper.git",
                EXTENSION_DIRECTORY + "sd-webui-aspect-ratio-helper"),
        )
    ),

    OptInfo(
        name="multi-subject-render",

        description="Generate multiple complex subjects all at once! First it "
        "creates your background image, then your foreground subjects, then does "
        "a depth analysis on them, cut their backgrounds, paste them onto your "
        "background and then does an img2img for a smooth blend! ",

        repos=(
            RepositoryInfo(
                "https://github.com/Extraltodeus/multi-subject-render.git",
                EXTENSION_DIRECTORY + "multi_subject_render"),
        )
    ),

    OptInfo(
        name="MiDaS",
        description="Compute depth from a single image",
        repos=(
            RepositoryInfo(
                "https://github.com/isl-org/MiDaS.git",
                EXTENSION_DIRECTORY + "midas"),)
    ),

    OptInfo(
        name="Auto SD Paint (krita)",
        description="",
        repos=(
            RepositoryInfo(
                "https://github.com/Interpause/auto-sd-paint-ext.git",
                EXTENSION_DIRECTORY + "auto-sd-paint-ext"),
            )
    ),


    OptInfo(
        name="SD Dynamic Thresholding",
        description="",
        repos=(
            RepositoryInfo(
                "https://github.com/mcmonkeyprojects/sd-dynamic-thresholding.git", 
                EXTENSION_DIRECTORY + "sd-dynamic-thresholding"),
            )
    ),

    OptInfo(
        name="Style Pile",
        description="",
        repos=(
            RepositoryInfo(
                "https://github.com/some9000/StylePile.git", 
                EXTENSION_DIRECTORY + "StylePile"),
            )
    ),

    OptInfo(
        name="Embedding Inspector",
        description="",
        repos=(
            RepositoryInfo(
                "https://github.com/tkalayci71/embedding-inspector.git", 
                EXTENSION_DIRECTORY + "embedding-inspector"),)
    ),

    OptInfo(
        name="prompt-fusion-extension",
        description="",
        repos=(
            RepositoryInfo(
                "https://github.com/ljleb/prompt-fusion-extension.git", 
                EXTENSION_DIRECTORY + "prompt-fusion-extension"),)
    ),


    OptInfo(
        name="Inpaint anything",
        description="",
        repos=(
            RepositoryInfo(
                "https://github.com/Uminosachi/sd-webui-inpaint-anything.git", 
                EXTENSION_DIRECTORY + "sd-webui-inpaint-anything"),)
    ),

    OptInfo(
        name="Dynamic prompts",
        description="",
        repos=(RepositoryInfo(
            "https://github.com/adieyal/sd-dynamic-prompts.git", 
            EXTENSION_DIRECTORY + "sd-dynamic-prompts"),)
    ),
]
