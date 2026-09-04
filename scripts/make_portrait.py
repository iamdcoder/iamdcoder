from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw
import random

BASE = Path(__file__).resolve().parent.parent

INPUT = BASE / "assets" / "portrait.jpg"
OUTPUT = BASE / "assets" / "portrait_glitch.gif"

WIDTH = 520
HEIGHT = 620

GRID_X = 104
GRID_Y = 124

FRAME_COUNT = 30

random.seed(42)


def prepare_image():
    image = Image.open(INPUT).convert("RGB")

    w, h = image.size

    # Crop the image so the portrait is centered.
    image = image.crop(
        (
            int(w * 0.05),
            int(h * 0.02),
            int(w * 0.95),
            int(h * 0.87)
        )
    )

    image = ImageEnhance.Contrast(image).enhance(1.2)

    image.thumbnail((WIDTH, HEIGHT))

    canvas = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (3, 7, 12)
    )

    x = (WIDTH - image.width) // 2
    y = (HEIGHT - image.height) // 2

    canvas.paste(image, (x, y))

    return canvas


def create_particles(image):

    small = image.resize(
        (GRID_X, GRID_Y),
        Image.Resampling.BILINEAR
    )

    particles = []

    for y in range(GRID_Y):

        for x in range(GRID_X):

            r, g, b = small.getpixel((x, y))

            brightness = (r + g + b) / 3

            if brightness > 15:

                particles.append(
                    (
                        x,
                        y,
                        r,
                        g,
                        b
                    )
                )

    random.shuffle(particles)

    return particles


def create_frame(particles, progress):

    frame = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (3, 7, 12)
    )

    draw = ImageDraw.Draw(frame)

    # Digital noise in the background.
    noise = int(900 * (1 - progress))

    for _ in range(noise):

        x = random.randrange(WIDTH)
        y = random.randrange(HEIGHT)

        value = random.randrange(15, 60)

        draw.rectangle(
            (
                x,
                y,
                x + 2,
                y + 2
            ),
            fill=(
                value // 2,
                value,
                min(90, value + 25)
            )
        )

    visible = int(len(particles) * progress)

    for x, y, r, g, b in particles[:visible]:

        target_x = int(x * WIDTH / GRID_X)
        target_y = int(y * HEIGHT / GRID_Y)

        # Particles begin scattered and gradually settle.
        spread = int((1 - progress) * 18)

        px = target_x + random.randint(
            -spread,
            spread
        )

        py = target_y + random.randint(
            -spread,
            spread
        )

        if px < 0 or px >= WIDTH:
            continue

        if py < 0 or py >= HEIGHT:
            continue

        color = (
            min(255, int(r * 0.9) + 15),
            min(255, int(g * 0.95) + 10),
            min(255, int(b * 1.05) + 10)
        )

        draw.rectangle(
            (
                px,
                py,
                px + 4,
                py + 4
            ),
            fill=color
        )

    # Scan line.
    if progress > 0.5:

        scan_y = int(
            ((progress - 0.5) / 0.5)
            * HEIGHT
        )

        draw.line(
            (
                0,
                scan_y,
                WIDTH,
                scan_y
            ),
            fill=(90, 220, 255),
            width=2
        )

    return frame


def main():

    if not INPUT.exists():

        print("ERROR:")
        print(f"Could not find {INPUT}")
        return

    image = prepare_image()

    particles = create_particles(image)

    frames = []

    for i in range(FRAME_COUNT):

        raw = i / (FRAME_COUNT - 1)

        # Smooth animation.
        progress = raw * raw * (3 - 2 * raw)

        frame = create_frame(
            particles,
            progress
        )

        frames.append(frame)

    # Keep the completed portrait on screen briefly.
    for _ in range(8):

        frames.append(
            frames[-1].copy()
        )

    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=80,
        loop=0
    )

    print()
    print("DONE!")
    print()
    print(f"Created:")
    print(OUTPUT)


if __name__ == "__main__":
    main()