import svgwrite
import base64

def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        #print(f'encoding {image_path}')
        return base64.b64encode(img_file.read()).decode('utf-8')


def build_map_image(output_filename, coord_list):
    width = '2400px'
    height = '1800px'

    filepath = 'static/images/'
    input_file = 'SY_base_map.svg.png'

    encoded_image = encode_image(filepath + input_file)

    dwg = svgwrite.Drawing(filepath + output_filename, size=(width, height))
    dwg.add(dwg.image(f'data:image/png;base64,{encoded_image}', size=(width, height), opacity=0.7))

    dwg.save()

    player_colors = ['slateblue', 'hotpink', 'purple', 'lightgreen', 'aqua', 'darkred']

    #print(coord_list)
    for i, c in enumerate(coord_list):
        #print(f'{output_filename}:  adding {player_colors[i]} marker @ {c}')
        marker = dwg.circle(center=c, r=15, fill=player_colors[i])
        dwg.add(marker)

    dwg.save()


def generate_new_map(players, G):
    # game_state is really just the players array

    public_output_file = 'public_map.svg'
    mrx_output_file = 'mrx_map.svg'

    public_locations = []
    private_locations = []

    for p in players:
        coords = G.nodes[p.position]["coords"]
        #print(p.mrx, p.name, p.position, coords)

        # the 17 - bit is because the row coordinates were initially defined from the bottom up
        translated_new_coords = (
                                 (coords[0] * 100) ,
                                 ((17 - coords[1]) * 100)
                                )

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


