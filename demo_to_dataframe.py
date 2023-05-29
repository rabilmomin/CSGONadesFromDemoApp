import pandas as pd


def get_dataframe_from_demo(parser, offset, scale):
    # All weapon_fire events (could have used grenade_thrown but doesn't work)
    events = parser.parse_events("weapon_fire", props=["X", "Y", "Z", "viewangle_pitch", "viewangle_yaw", "team_num"])
    df_weapon_fire = pd.DataFrame(events)

    # Get all weapon_fire events that are utility
    df_utility = df_weapon_fire[(df_weapon_fire["weapon"] == "weapon_flashbang")
                                | (df_weapon_fire["weapon"] == "weapon_incgrenade")
                                | (df_weapon_fire["weapon"] == "weapon_molotov")
                                | (df_weapon_fire["weapon"] == "weapon_smokegrenade")
                                | (df_weapon_fire["weapon"] == "weapon_hegrenade")].copy()

    # Using player position apply offset and scaling to match position on radar
    df_utility['map_player_X'] = (df_utility["player_X"] - offset[0]) * (1 / scale)
    df_utility['map_player_Y'] = (df_utility["player_Y"] - offset[1]) * -(1 / scale)

    # Split df_utility into each of its individual utility types
    df_flashes_thrown = df_utility[(df_utility["weapon"] == "weapon_flashbang")]
    df_hegrenades_thrown = df_utility[(df_utility["weapon"] == "weapon_hegrenade")]
    df_smokegrenades_thrown = df_utility[(df_utility["weapon"] == "weapon_smokegrenade")]
    df_molotovs_thrown = df_utility[(df_utility["weapon"] == "weapon_molotov")
                                    | (df_utility["weapon"] == "weapon_incgrenade")]

    # Set up dictionary for data frames based on player_name
    df_utility = dict(tuple(df_utility.groupby('player_name')))
    df_flashes_thrown = dict(tuple(df_flashes_thrown.groupby('player_name')))
    df_hegrenades_thrown = dict(tuple(df_hegrenades_thrown.groupby('player_name')))
    df_smokegrenades_thrown = dict(tuple(df_smokegrenades_thrown.groupby('player_name')))
    df_molotovs_thrown = dict(tuple(df_molotovs_thrown.groupby('player_name')))

    # Parse detonation events for each utility to get position of detonation
    events = parser.parse_events("flashbang_detonate")
    df_flashbang_detonate = pd.DataFrame(events)
    df_flashbang_detonate["map_det_X"] = (df_flashbang_detonate["x"] - offset[0]) * (1 / scale)
    df_flashbang_detonate["map_det_Y"] = (df_flashbang_detonate["y"] - offset[1]) * -(1 / scale)

    events = parser.parse_events("hegrenade_detonate")
    df_hegrenade_detonate = pd.DataFrame(events)
    df_hegrenade_detonate["map_det_X"] = (df_hegrenade_detonate["x"] - offset[0]) * (1 / scale)
    df_hegrenade_detonate["map_det_Y"] = (df_hegrenade_detonate["y"] - offset[1]) * -(1 / scale)

    events = parser.parse_events("smokegrenade_detonate")
    df_smokegrenade_detonate = pd.DataFrame(events)
    df_smokegrenade_detonate["map_det_X"] = (df_smokegrenade_detonate["x"] - offset[0]) * (1 / scale)
    df_smokegrenade_detonate["map_det_Y"] = (df_smokegrenade_detonate["y"] - offset[1]) * -(1 / scale)

    # events = parser.parse_events("molotov_detonate") #game event molotov_detonate does not exist or is broken
    # df_molotov_detonate = pd.DataFrame(events)

    # Set up dictionary for data frames based on player_name
    df_flashbang_detonate = dict(tuple(df_flashbang_detonate.groupby('player_name')))
    df_hegrenade_detonate = dict(tuple(df_hegrenade_detonate.groupby('player_name')))
    df_smokegrenade_detonate = dict(tuple(df_smokegrenade_detonate.groupby('player_name')))
    # df_molotov_detonate = dict(tuple(df_molotov_detonate.groupby('player_name')))

    # Pair weapon_fire events and detonation events into a new dataframe
    df_flashes = pd.DataFrame()
    df_nades = pd.DataFrame()
    df_smokes = pd.DataFrame()
    for k in df_utility.keys():
        if k in df_flashes_thrown:
            df_flashes = pd.concat([df_flashes, (pd.concat([df_flashes_thrown[k].reset_index(drop=True),
                                                            df_flashbang_detonate[k].reset_index(drop=True)[
                                                                ["x", "y", "z", "map_det_X", "map_det_Y"]]], axis=1))])
        if k in df_hegrenades_thrown:
            df_nades = pd.concat([df_nades, (pd.concat([df_hegrenades_thrown[k].reset_index(drop=True),
                                                        df_hegrenade_detonate[k].reset_index(drop=True)[
                                                            ["x", "y", "z", "map_det_X", "map_det_Y"]]], axis=1))])
        if k in df_smokegrenades_thrown:
            df_smokes = pd.concat([df_smokes, (pd.concat([df_smokegrenades_thrown[k].reset_index(drop=True),
                                                          df_smokegrenade_detonate[k].reset_index(drop=True)[
                                                              ["x", "y", "z", "map_det_X", "map_det_Y"]]], axis=1))])

    df_utility = pd.concat([df_flashes.reset_index(), df_nades.reset_index(), df_smokes.reset_index()])
    df_utility = df_utility.dropna()

    return df_utility
