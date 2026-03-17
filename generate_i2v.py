import argparse
from pathlib import Path

import torch
from PIL import Image
from diffusers import CogVideoXImageToVideoPipeline
from diffusers.utils import export_to_video


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, required=True, help="Path to input image")
    parser.add_argument("--prompt_file", type=str, required=True, help="Path to prompt txt")
    parser.add_argument("--output", type=str, default="output/base_video.mp4")
    parser.add_argument("--model", type=str, default="THUDM/CogVideoX-5b-I2V")
    parser.add_argument("--frames", type=int, default=81)
    parser.add_argument("--fps", type=int, default=16)
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--guidance", type=float, default=6.0)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    image_path = Path(args.image)
    prompt_path = Path(args.prompt_file)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt = f.read().strip()

    image = Image.open(image_path).convert("RGB")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    print(f"Loading model: {args.model}")
    pipe = CogVideoXImageToVideoPipeline.from_pretrained(
        args.model,
        torch_dtype=dtype
    )

    if device == "cuda":
        pipe.to("cuda")
        try:
            pipe.enable_model_cpu_offload()
        except Exception:
            pass
    else:
        pipe.to("cpu")

    generator = torch.Generator(device=device).manual_seed(args.seed)

    print("Generating frames...")
    result = pipe(
        prompt=prompt,
        image=image,
        num_frames=args.frames,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        generator=generator,
    )

    frames = result.frames[0]

    print(f"Exporting silent base video to: {output_path}")
    export_to_video(frames, str(output_path), fps=args.fps)
    print("Done.")


if __name__ == "__main__":
    main()
