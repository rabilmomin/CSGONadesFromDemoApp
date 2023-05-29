import os
from functools import partial
from tkinter import *
from tkinter import filedialog

import matplotlib.pyplot as plt
import pandas as pd
from demoparser import DemoParser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from demo_to_dataframe import get_dataframe_from_demo
from radar_resources_parser import get_radar_resources


class Window:
    def __init__(self, ext_root):

        self.root = ext_root
        self.root.title("CSGO Utility Visualizer")
        self.root.geometry("800x800")

        self.demo_dir = ""
        self.radar_dir = ""
        self.df_utility = pd.DataFrame()
        self.map_attributes = {}
        self.radar_path = ""
        self.radar_path_lower = ""

        # region Setup tkinter Frames and widgets
        self.top_frame = Frame(self.root, width=800, height=200)
        self.top_frame.pack(side="top", fill="x", padx=10, pady=5, expand=False)
        self.top_frame.grid_columnconfigure((0, 3), weight=1)

        self.mid_frame = Frame(self.root, width=800, height=100)
        self.mid_frame.pack(side="top", fill="x", padx=10, pady=5, expand=False)
        self.mid_frame.grid_columnconfigure((0, 5), weight=1)

        self.radar_frame = Frame(self.root, width=800, height=600, bg="white")
        self.radar_frame.pack(side="bottom", fill="both", padx=10, pady=5, expand=True)
        self.radar_frame.grid_columnconfigure(0, weight=1, uniform="1")

        Label(self.top_frame, text="CSGO Utility Visualizer").grid(row=0, column=1, columnspan=2, sticky="ew")

        self.demo_label = Label(self.top_frame, text="Current Demo:")
        self.demo_label.grid(row=1, column=1, columnspan=2, sticky="ew")

        self.select_demo_button = Button(self.top_frame, text="Select Demo File", command=self.select_demo)
        self.select_demo_button.grid(row=2, column=1, padx=5, pady=5, sticky="")

        self.select_radar_dir_button = Button(self.top_frame, text="Select Radar Folder",
                                              command=self.select_radar_dir)
        self.select_radar_dir_button.grid(row=2, column=2, padx=5, pady=5, sticky="")

        self.plot_button = Button(self.top_frame, text="Parse Demo", command=self.get_df)
        self.plot_button.grid(row=3, column=1, columnspan=2,pady=5, sticky="")

        Label(self.mid_frame, text="Player:").grid(row=0, column=1)
        self.player_clicked = StringVar()
        self.player_clicked.set("")
        self.players_menu = OptionMenu(self.mid_frame,
                                       self.player_clicked,
                                       *[""])
        self.players_menu.grid(row=1, column=1, padx=5)

        Label(self.mid_frame, text="Utility: ").grid(row=0, column=2)
        self.utility_clicked = StringVar()
        self.utility_clicked.set("")
        self.utility_menu = OptionMenu(self.mid_frame,
                                       self.utility_clicked,
                                       *[""])
        self.utility_menu.grid(row=1, column=2, padx=5)

        Label(self.mid_frame, text="Round: ").grid(row=0, column=3)
        self.round_clicked = IntVar()
        self.round_clicked.set(0)
        self.round_menu = OptionMenu(self.mid_frame,
                                     self.round_clicked,
                                     *["0"])
        self.round_menu.grid(row=1, column=3, padx=5)

        self.search_button = Button(self.mid_frame, text="Search")
        self.search_button.grid(row=0, column=4, rowspan=2, padx=5)
        # endregion

    # Function for the select demo button
    def select_demo(self):
        self.demo_dir = filedialog.askopenfilename(initialdir=os.getcwd(),
                                                   title="Select Demo",
                                                   filetypes=[("Demo Files", "*.dem")])

    # Function for the select radar directory button
    def select_radar_dir(self):
        self.radar_dir = filedialog.askdirectory(initialdir=os.getcwd(),
                                                 title="Select Radar Directory")

    # Function for the Parse Demo Button
    def get_df(self):
        # check if the user input a demo and radar directory
        if self.demo_dir == "":
            self.demo_label.config(text=f"Current Demo: Missing Demo File")
            return
        if self.radar_dir == "":
            self.demo_label.config(text=f"Current Demo: Missing Radar Directory")
            return

        # Try to parse the demo. If it fails then display an error in the demo_label
        try:
            parser = DemoParser(self.demo_dir)
            demo_name = self.demo_dir.split('/')[-1]
            self.demo_label.config(text=f"Current Demo: {demo_name}")
        except RuntimeError:
            self.demo_label.config(text=f"Current Demo: Invalid demo file")
            return

        map_name = parser.parse_header()['map_name']
        map_name = map_name.rstrip('\x00')
        self.radar_path = self.radar_dir + f'\\{map_name}_radar.dds'

        # Try to parse the map.txt file and if it fails then return an error in the demo_label
        try:
            self.map_attributes = get_radar_resources(self.radar_dir, map_name)
        except IOError:
            self.demo_label.config(text=f"Current Demo: Invalid Radar Directory")
            return

        # If we parsed that the map is multi level then get the maps lower radar
        if self.map_attributes["multi_level_flag"]:
            self.radar_path_lower = self.radar_dir + f'\\{map_name}_lower_radar.dds'

        # Using the parser get df_utility which is needed for plots
        df_utility = get_dataframe_from_demo(parser,
                                             [self.map_attributes["pos_x"], self.map_attributes["pos_y"]],
                                             self.map_attributes["scale"])
        # Make sure we are working on a copy not a view.
        self.df_utility = df_utility.copy()

        # region Get rid of previous drop down menus and recreate them with values parsed from df_utility
        self.players_menu.destroy()
        self.player_clicked = StringVar()
        self.player_clicked.set(self.df_utility["player_name"].unique()[0])
        self.players_menu = OptionMenu(self.mid_frame,
                                       self.player_clicked,
                                       *(list(self.df_utility["player_name"].unique()) + ["All"]))
        self.players_menu.grid(row=1, column=1, padx=5)

        self.utility_menu.destroy()
        self.utility_clicked = StringVar()
        self.utility_clicked.set("Flashbang")
        self.utility_menu = OptionMenu(self.mid_frame,
                                       self.utility_clicked,
                                       *['Grenade', 'Smoke', 'Flashbang'])

        self.utility_menu.grid(row=1, column=2, padx=5)

        self.round_menu.destroy()
        self.round_clicked = IntVar()
        self.round_clicked.set(0)
        self.round_menu = OptionMenu(self.mid_frame,
                                     self.round_clicked,
                                     *list(range(0, int(self.df_utility["round"].max()) + 1)))

        self.round_menu.grid(row=1, column=3, padx=5)

        # Initial search button does nothing now we assign a function to it when a demo is parsed.
        self.search_button.destroy()
        self.search_button = Button(self.mid_frame, text="Search",
                                    command=partial(self.plot_function_simple,
                                                    self.df_utility,
                                                    self.player_clicked,
                                                    self.utility_clicked,
                                                    self.round_clicked))
        self.search_button.grid(row=0, column=4, rowspan=2, padx=5)
        # endregion

        # If the canvas used for plotting already exists then get rid of it.
        # This is so we can clear out the old canvas and old plots for new ones.
        try:
            self.canvas.get_tk_widget().pack_forget()
            del self.canvas
        except AttributeError:
            pass

    def plot_function_simple(self, df_util_ext, player_name, nade_type, game_round):
        weapon_mapping = {"Grenade": "weapon_hegrenade", "Smoke": "weapon_smokegrenade",
                          "Flashbang": "weapon_flashbang"}

        # These are tkinter variables and need to be cast into normal variables
        player_name = player_name.get()
        nade_type = nade_type.get()
        game_round = game_round.get()

        weapon_name = weapon_mapping[nade_type]

        df_util = df_util_ext

        # If an existing plot exists then clear it
        try:
            self.ax1.clear()
        except AttributeError:
            pass

        try:
            self.ax2.clear()
        except AttributeError:
            pass

        if player_name != "All":
            df_util = df_util[(df_util["player_name"] == player_name)]

        df_util = df_util[df_util["weapon"] == weapon_name]

        if game_round != 0:
            df_util = df_util[(df_util["round"] == game_round)]

        # region Plotting for multiple levels
        if self.map_attributes["multi_level_flag"]:
            self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2,
                                                          figsize=(self.radar_frame.winfo_width() / 100,
                                                                   self.radar_frame.winfo_height() / 100),
                                                          dpi=100)

            # Plot the both radars
            im = plt.imread(self.radar_path)
            self.ax1.imshow(im)
            im_lower = plt.imread(self.radar_path_lower)
            self.ax2.imshow(im_lower)

            # 2:T-side:gold 3:CT-side:blue
            team_colors = {2: "gold", 3: "blue"}

            util_colors = {"weapon_flashbang": "yellow", "weapon_smokegrenade": "white", "weapon_hegrenade": "orange"}

            # Split df_util into df_util_upper df_util_lower based on where the utility detonated
            df_util_upper = df_util[df_util["z"] > self.map_attributes["AltitudeMax"]]
            df_util_lower = df_util[df_util["z"] <= self.map_attributes["AltitudeMax"]]

            # region Plot the upper or default radar points
            # Plot a connecting line between the player and utility detonation point
            self.ax1.plot([df_util_upper["map_player_X"], df_util_upper["map_det_X"]],
                          [df_util_upper["map_player_Y"], df_util_upper["map_det_Y"]],
                          color="white",
                          linestyle="--",
                          alpha=0.5)

            # Plot the position the player is at
            self.ax1.scatter(df_util_upper["map_player_X"],
                             df_util_upper["map_player_Y"],
                             c=df_util_upper["player_team_num"].map(team_colors))

            # Plot the position the utility detonated at
            self.ax1.scatter(df_util_upper["map_det_X"],
                             df_util_upper["map_det_Y"],
                             c=df_util_upper["weapon"].map(util_colors), marker="*")

            self.ax1.axis("off")
            self.ax1.title.set_text(f'{self.map_attributes["map_name"]} upper utility')
            # endregion

            # region Plot the lower radar points
            self.ax2.plot([df_util_lower["map_player_X"], df_util_lower["map_det_X"]],
                          [df_util_lower["map_player_Y"], df_util_lower["map_det_Y"]],
                          color="white",
                          linestyle="--",
                          alpha=0.5)

            self.ax2.scatter(df_util_lower["map_player_X"],
                             df_util_lower["map_player_Y"],
                             c=df_util_lower["player_team_num"].map(team_colors))

            self.ax2.scatter(df_util_lower["map_det_X"],
                             df_util_lower["map_det_Y"],
                             c=df_util_lower["weapon"].map(util_colors), marker="*")

            self.ax2.axis("off")
            self.ax2.title.set_text(f'{self.map_attributes["map_name"]} lower utility')
            # endregion
        # endregion
        # region Plotting a single level
        else:
            self.fig, self.ax1 = plt.subplots(figsize=(self.radar_frame.winfo_width() / 100,
                                                       self.radar_frame.winfo_height() / 100),
                                              dpi=100)
            im = plt.imread(self.radar_path)
            self.ax1.imshow(im)

            self.ax1.plot([df_util["map_player_X"], df_util["map_det_X"]],
                          [df_util["map_player_Y"], df_util["map_det_Y"]],
                          color="white",
                          linestyle="--",
                          alpha=0.5)

            team_colors = {2: "gold", 3: "blue"}
            self.ax1.scatter(df_util["map_player_X"],
                             df_util["map_player_Y"],
                             c=df_util["player_team_num"].map(team_colors))

            util_colors = {"weapon_flashbang": "yellow", "weapon_smokegrenade": "white", "weapon_hegrenade": "orange"}
            self.ax1.scatter(df_util["map_det_X"],
                             df_util["map_det_Y"],
                             c=df_util["weapon"].map(util_colors), marker="*")

            self.ax1.axis("off")
            self.ax1.title.set_text(f'{self.map_attributes["map_name"]} utility')
        # endregion

        # If the canvas exists then reassign the figure else set up the figure
        try:
            self.canvas.figure = self.fig
        except AttributeError:
            self.canvas = FigureCanvasTkAgg(self.fig, self.radar_frame)
            self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # Draw what's on the canvas to the frame
        self.canvas.draw()


if __name__ == "__main__":
    root = Tk()
    gui = Window(root)
    gui.root.mainloop()
