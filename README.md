# Better Color Cycler (Original)


**The problem:**
-
The built-in shortcuts to shift the color hue is too inconsistent.
The brightness of the color would drift into total darkness after enough full rotations.

It's impossible to change the color with shortcuts if saturation is 0 until you manually change it.

**The solution:**
-
This plugin adds shortcuts to enhance the ability to rotate the hue of the current foreground color,
with a fixed angle of rotation and not changing the color's saturation or brightness (value).

Additionally, you can configure how many steps (number of times the shortcuts are triggered) are needed to make a full rotation in the color wheel,
so you can choose to pick a color of a specific angle if you use a dial accessory or similar.

Example: By default, max_steps is set to 24, because the "Mini KeyDial KD100", takes 24 steps to make a full rotation.
You can edit this value in the .py file if you use similar accessories.
#
*Extra features:*

Shortcuts to adjust saturation and brightness with a fixed distance, which don't drift.


*Download Old Version*
-
[Download here](https://bitbucket.org/simolette/krita_bettercolorcycler/get/HEAD.zip)


*Usage*
-
Once the plugin is installed you can configure shortcuts in krita settings, like you would with other shortcuts.

You can also change the default settings inside the .py file if you want.

#
*Relative mode:*

With any color you have currently selected, rotate the hue by a certain degree.
The default angle is 15° but this can be changed in the .py file.

#
*Absolute mode:*

Calibrate the accessory of choice (turn dial to 12-o'clock position, then use the shortcut to reset the counter. Then set Shortcuts 3 and 4.


#
*Shortcuts*

- Shortcut 1:	Shift hue counter-clockwise (relative to current color)
- Shortcut 2:	Shift hue clockwise (relative to current color)
- Shortcut 3:	Shift hue counter-clockwise (absolute mode)
- Shortcut 4:	Shift hue clockwise (absolute mode)
- Shortcut 5:	Reset the step counter (absolute mode)
- Shortcut 6:	Toggle fine mode

Default shortcuts: Ctrl + Shift + 1-6

*Extra Shortcuts*

- Shortcut 7:	Decrease saturation
- Shortcut 8:	Increase saturation
- Shortcut 9:	Decrease brightness (value)
- Shortcut 10:	Increase brightness (value)


# Better Color Cycler (Modifications):

# V 1.0
- Fix math formula using depercated library.
- Fix shortcuts not showing.
- Fix shortcuts group.
- Added persistant values (Remember last values set after restarting Krita)
- Added popup showing changes applied.
- Added a docker panel to configure the amount of steps that takes to travel the full range of the HUE, Saturation, and Value.

# V 2.0
- Fixed jump to previous storaged color after using color picker then shortcut.
- Fixed HUE value storage and update.
- Other fixes.

*Download Latest Version*
[Download](https://github.com/loudbeatproductions/BetterColorCycler-for-Krita/archive/refs/heads/main.zip)
