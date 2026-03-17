import argparse
import subprocess
from pathlib import Path
import shlex


def run(cmd):
    print("Running:")
    print(" ".join(shlex.quote(c) for c in cmd))
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_video", type=str, required=True)
    parser.add_argument("--audio", type=str, required=True)
    parser.add_argument("--output", type=str, default="output/final_video.mp4")
    parser.add_argument("--font", type=str, default="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf")
    parser.add_argument("--duration", type=float, default=5.0)
    args = parser.parse_args()

    input_video = Path(args.input_video)
    audio = Path(args.audio)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    alpha_expr = (
        "if(lt(t,3),0,"
        "if(lt(t,3.35),(t-3)/0.35,"
        "if(lt(t,4.65),1,"
        "if(lt(t,5),(5-t)/0.35,0))))"
    )

    title = (
        f"drawtext=fontfile='{args.font}':"
        f"text='Happy St. Patrick\\'s Day':"
        f"fontcolor=0xD4AF37:"
        f"fontsize=52:"
        f"x=(w-text_w)/2:"
        f"y=h*0.78:"
        f"alpha='{alpha_expr}':"
        f"borderw=2:"
        f"bordercolor=0x1f4d1f@0.45:"
        f"shadowx=0:shadowy=0"
    )

    glow = (
        f"drawtext=fontfile='{args.font}':"
        f"text='Happy St. Patrick\\'s Day':"
        f"fontcolor=0x66ff99@0.28:"
        f"fontsize=56:"
        f"x=(w-text_w)/2:"
        f"y=h*0.777:"
        f"alpha='{alpha_expr}'"
    )

    shamrock_left = (
        f"drawtext=fontfile='{args.font}':"
        f"text='☘':"
        f"fontcolor=0x66ff66:"
        f"fontsize=34:"
        f"x=w*0.16:"
        f"y=h*0.775:"
        f"alpha='{alpha_expr}'"
    )

    shamrock_right = (
        f"drawtext=fontfile='{args.font}':"
        f"text='☘':"
        f"fontcolor=0x66ff66:"
        f"fontsize=34:"
        f"x=w*0.84:"
        f"y=h*0.775:"
        f"alpha='{alpha_expr}'"
    )

    grain = "noise=alls=6:allf=t"

    vf = ",".join([grain, glow, title, shamrock_left, shamrock_right])

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(input_video),
        "-i", str(audio),
        "-filter_complex", vf,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-t", str(args.duration),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(output)
    ]

    run(cmd)
    print(f"Created: {output}")


if __name__ == "__main__":
    main()
