def get_radar_resources(radar_dir, map_name):
    radar_txt_path = radar_dir + f'\\{map_name}.txt'

    map_attributes = {"map_name": map_name, "multi_level_flag": False}

    # Parse the map_name.txt file for important attributes regarding plotting.
    try:
        with open(radar_txt_path) as fh:
            for line in fh:
                line = line.split()
                for k in range(len(line)):
                    if line[k] == '//':
                        line = line[0:k]
                        break
                if len(line) == 1 and line[0].strip('\"') == "verticalsections":
                    map_attributes["multi_level_flag"] = True
                if len(line) > 1:
                    map_attributes[line[0].strip('\"')] = line[1].strip('\"')

        if map_attributes["multi_level_flag"]:
            map_attributes["AltitudeMax"] = float(map_attributes["AltitudeMax"])

        map_attributes["pos_x"] = float(map_attributes["pos_x"])
        map_attributes["pos_y"] = float(map_attributes["pos_y"])
        map_attributes["scale"] = float(map_attributes["scale"])
    except RuntimeError:
        print("Cannot find overview file or invalid formatting.")

    return map_attributes
