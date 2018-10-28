import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def get_valid_code_img(request):
    img = Image.new('RGB', (260, 32), color=get_random_color())
    draw = ImageDraw.Draw(img)
    fontO = ImageFont.truetype("static/font/Outwrite.ttf", size=30)
    valid_code_str = ""
    for i in range(5):
        random_num = str(random.randint(0, 9))
        random_low_alpha = chr(random.randint(95, 122))
        random_upper_alpha = chr(random.randint(65, 90))
        random_chr = random.choice([random_num, random_low_alpha, random_upper_alpha])
        draw.text((i * 38 + 20, 0), random_chr, get_random_color(), font=fontO)
        valid_code_str += random_chr
    # print(valid_code_str)
    width = 260
    height = 32
    for i in range(3):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=get_random_color())
    for i in range(10):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random_color())
    # with open('validCode.png', 'wb') as f:
    #     img.save(f, "png")
    # with open('validCode.png', 'rb') as f:
    #     data = f.read()
    f = BytesIO()
    img.save(f, 'png')
    data = f.getvalue()
    request.session["valid_code_str"] = valid_code_str
    '''
    数据保存到session中
    '''
    return data
