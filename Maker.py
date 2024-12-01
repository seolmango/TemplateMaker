from PIL import Image, ImageDraw, ImageFont
COLOR_ACCENT = "#E63946"
COLOR_BACKGROUND = "#F1FAEE"
COLOR_MAIN = "#A8DADC"
COLOR_DARKER = "#457B9D"
COLOR_TEXT = "#000000"

FONT_PATH_LIGHT = './assets/SB 어그로 L.ttf'
FONT_PATH_MEDIUM = './assets/SB 어그로 M.ttf'
FONT_PATH_BOLD = './assets/SB 어그로 B.ttf'

def make_base(number, info):
  width, height = 1080, 1080
  grid_size = 80

  image = Image.new("RGB", (width, height), COLOR_MAIN)
  draw = ImageDraw.Draw(image)

  for x in range(20, width, grid_size):
    draw.line((x, 0, x, height), fill=COLOR_DARKER, width=2)
  for y in range(20, height, grid_size):
    draw.line((0, y, width, y), fill=COLOR_DARKER, width=2)

  rect_width, rect_height = 1000, 1000
  left = (width - rect_width) // 2
  top = (height - rect_height) // 2
  right = left + rect_width
  bottom = top + rect_height
  draw.rectangle([left, top, right, bottom], fill=COLOR_BACKGROUND)

  draw.line((90,90,width-90, 90), fill=COLOR_TEXT, width=2)
  draw.line((90,150,width-90, 150), fill=COLOR_TEXT, width=2)

  text_title_font = ImageFont.truetype(FONT_PATH_LIGHT, 25)

  draw.text((95,125), f"No. {number:03d}", fill=COLOR_TEXT, anchor="lm", font=text_title_font)
  draw.text((width-95,125), f"{info}", fill=COLOR_TEXT, anchor="rm", font=text_title_font)

  return image, draw


def title_page(save_path, number, artist, album, nickname):
    width = 1080
    image, draw = make_base(number, "@idont_knowmusic")

    text_artist_font = ImageFont.truetype(FONT_PATH_MEDIUM, 100)

    album_text_lines = wrap_text(album, 13)
    draw.text((95, 250), f"{artist}", fill=COLOR_TEXT, font=text_artist_font, anchor="lm")
    for i, lines in enumerate(album_text_lines):
        draw.text((95, 375 + (125 * i)), f"{lines.strip(' ')}", fill=COLOR_ACCENT, font=text_artist_font, anchor="lm")

    draw.line((90, 330 + (125 * len(album_text_lines)), width - 90, 330 + (125 * len(album_text_lines))),
              fill=COLOR_TEXT, width=2)
    draw.text((985, 375 + (125 * len(album_text_lines))), f"by. {nickname}", fill=COLOR_TEXT,
              font=ImageFont.truetype(FONT_PATH_MEDIUM, 35), anchor="rm")

    more_text_font = ImageFont.truetype(FONT_PATH_LIGHT, 25)
    draw.text((95, 940), f"이 리뷰는 정답이 아니며 수많은 관점 중 하나일 뿐입니다", fill=COLOR_TEXT, anchor="lm", font=more_text_font)
    draw.text((95, 985), f"여러분의 음악에 대한 감상과 감정은 그 자체로 존중받아야 합니다", fill=COLOR_TEXT, anchor="lm", font=more_text_font)

    image.save(f"{save_path}/0.png")

def mood_page(save_path, number, cover, title, artist, song_count, time, when, genre, why):
    image, draw = make_base(number, "@idont_knowmusic")

    cover_image = Image.open(cover)
    cover_image = cover_image.resize([400,400])
    draw.rectangle([90, 180, 510, 600], fill=COLOR_TEXT)
    draw.rectangle([95, 185, 505, 595], fill=COLOR_BACKGROUND)

    image.paste(cover_image, (100, 190))

    album_text_lines = wrap_text(title, 13)
    for i, lines in enumerate(album_text_lines):
      draw.text((550, 210 + (80*i)), f"{lines.strip(' ')}", fill=COLOR_TEXT, font=ImageFont.truetype(FONT_PATH_LIGHT, 70), anchor="lm")

    infos_text_lines = [f"아티스트", f"수록곡", f"재생 시간", f"발매일", f"장르"]
    start_y = 625 - (45 * len(infos_text_lines))
    for i, lines in enumerate(infos_text_lines):
      draw.text((550, start_y + (45*i)), f"{lines.strip(' ')}", fill=COLOR_ACCENT, font=ImageFont.truetype(FONT_PATH_LIGHT, 40), anchor="lm")

    infos_text_lines = [f"{artist}", f"{song_count}곡", f"{time}", f"{when}", f"{genre}"]
    start_y = 625 - (45 * len(infos_text_lines))
    for i, lines in enumerate(infos_text_lines):
      draw.text((750, start_y + (45*i)), f"{lines.strip(' ')}", fill=COLOR_TEXT, font=ImageFont.truetype(FONT_PATH_LIGHT, 30), anchor="lm")

    draw.text((90, 650), f"선정 이유", fill=COLOR_ACCENT, font=ImageFont.truetype(FONT_PATH_LIGHT, 40), anchor="lm")

    why_text_lines = wrap_text(why, 30)
    for i, lines in enumerate(why_text_lines):
      draw.text((90, 700 + (45*i)), f"{lines.strip(' ')}", fill=COLOR_TEXT, font=ImageFont.truetype(FONT_PATH_LIGHT, 40), anchor="lm")
    image.save(f"{save_path}/1.png")


def wrap_text(text, max_length):
    lines = []
    paragraphs = text.split('\n')

    for paragraph in paragraphs:
        if paragraph == '':
            lines.append('')
        while paragraph:
            if len(paragraph) > max_length:
                space_index = paragraph[:max_length + 1].rfind(' ')
                if space_index != -1:
                    lines.append(paragraph[:space_index])
                    paragraph = paragraph[space_index + 1:]
                else:
                    lines.append(paragraph[:max_length])
                    paragraph = paragraph[max_length:]
            else:
                lines.append(paragraph)
                break
    return lines

def list_page(save_path, number, track_list):
    image, draw = make_base(number, "@idont_knowmusic")
    draw.text((90, 190), f"트랙 리스트", fill=COLOR_ACCENT, font=ImageFont.truetype(FONT_PATH_LIGHT, 40), anchor="lm")

    text_lines = [[],[],[],[]]
    for track in track_list:
      text_lines[track['disc']-1].append([track['order'],track['title'],track['is_title']])
    draw.text((90, 250), f"CD1", fill=COLOR_ACCENT, font=ImageFont.truetype(FONT_PATH_LIGHT, 30), anchor="lm")
    y = 300
    for track in text_lines[0]:
      temp = f"{track[0]}. {track[1]}" + ("{Title}" if track[2] else "")
      if len(text_lines[1]) != 0:
        draw.text((540, 250), f"CD2", fill=COLOR_ACCENT, font=ImageFont.truetype(FONT_PATH_LIGHT, 30), anchor="lm")
        temp = wrap_text(temp, 22)
        for line in temp:
          draw.text((90, y), line, fill=COLOR_ACCENT if track[2] else COLOR_TEXT, font=ImageFont.truetype(FONT_PATH_LIGHT, 30), anchor="lm")
          y += 40
      else:
        temp = wrap_text(temp, 40)
        for line in temp:
          draw.text((90, y), line, fill=COLOR_ACCENT if track[2] else COLOR_TEXT, font=ImageFont.truetype(FONT_PATH_LIGHT, 40), anchor="lm")
          y += 45
    y = 300
    for track in text_lines[1]:
      temp = f"{track[0]}. {track[1]}" + ("{Title}" if track[2] else "")
      temp = wrap_text(temp, 22)
      for line in temp:
        draw.text((540, y), line, fill=COLOR_ACCENT if track[2] else COLOR_TEXT, font=ImageFont.truetype(FONT_PATH_LIGHT, 30), anchor="lm")
        y += 40

    image.save(f"{save_path}/2.png")