import svgwrite
import base64


def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def build_map_image(output_filename, coord_list):
    width = '2400px'
    height = '1800px'

    filepath = 'static/images/'
    input_file = 'SY_base_map.svg.png'

    encoded_image = encode_image(filepath + input_file)

    dwg = svgwrite.Drawing(filepath + output_filename, size=(width, height))
    dwg.add(dwg.image(f'data:image/png;base64,{encoded_image}', size=(width, height), opacity=0.99))

    dwg.save()

    #player_colors = ['slateblue', 'hotpink', 'purple', 'aqua', 'darkred', 'lightgreen']

    # if 2 people are on the same spot, we make the circle's progressively bigger
    collisions = {}

    for i, c in enumerate(coord_list):
        if c[:2] != (0, 0):
            collisions[c] = collisions.get(c, 0) + 1

            marker_ring = dwg.circle(center=c[:2], r=(55 + (collisions[c] * 10)), stroke=c[2], stroke_width=12, fill='none')
            dwg.add(marker_ring)

    dwg.save()


def generate_new_map(players, G):
    # game_state is really just the players array

    public_output_file = 'public_map.svg'
    mrx_output_file = 'mrx_map.svg'

    public_locations = []
    private_locations = []

    for p in players:
        coords = G.nodes[p.position]["coords"]

        # the 17 - bit is because the row coordinates were initially defined from the bottom up
        # somehow the stops on the image are perfectly on a 100x100 grid
        # also stick the player color in there to properly colorize the map markers
        translated_new_coords = (
                                 (coords[0] * 100) ,
                                 ((17 - coords[1]) * 100),
                                 p.color,
                                )

        print(type(translated_new_coords))

        if p.mrx and p.visible_location:
            private_locations.append(translated_new_coords)
            public_locations.append(translated_new_coords)

        elif p.mrx and not p.visible_location:
            private_locations.append(translated_new_coords)
            public_locations.append((0.0, 0.0))

        elif p.detective:
            private_locations.append(translated_new_coords)
            public_locations.append(translated_new_coords)

    build_map_image(public_output_file, public_locations)
    build_map_image(mrx_output_file, private_locations)


