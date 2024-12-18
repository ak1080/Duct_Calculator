from fluid_equations import darcy_weisbach, colebrook_white_solver_fsolve, reynolds_num
from math import pi
import tkinter as tk
from tkinter import ttk, messagebox, font

"""
By: Alex Kalmbach
Date: 12/17/2024
Description: GUI for evaluating the performance of user chosen duct sizes.
"""

SHEET_METAL_EPSILON = 0.0007  # 0.0005 is typical of sheet metal. 0.0007 seems to match McQuay's sizer (more conservative).
AIR_DYN_VISC = 0.0432  # lbm/(ft·h) at 68°F and sea level.
AIR_DENSITY = 0.075  # lbm/ft³ at 68°F and sea level.

def clear_output(*args):
    result.set("")
    air_properties.set("")

def update_fields(*args):
    """Makes it so user can only enter dimensions for the duct shape selected"""
    clear_output()
    duct_shape = duct_shape_var.get()
    if duct_shape == "Round":
        round_diameter_entry.config(state="normal", background="white")
        rect_width_entry.config(state="disabled", background="#d1d9e6")
        rect_height_entry.config(state="disabled", background="#d1d9e6")
        rect_width_entry.delete(0, tk.END)
        rect_height_entry.delete(0, tk.END)
    elif duct_shape == "Rectangular":
        round_diameter_entry.config(state="disabled", background="#d1d9e6")
        round_diameter_entry.delete(0, tk.END)
        rect_width_entry.config(state="normal", background="white")
        rect_height_entry.config(state="normal", background="white")

def calculate(*args):
    """Calculates fluid performance based on duct shape and user inputs."""
    try:
        cfm = float(cfm_entry.get().strip())
        duct_shape = duct_shape_var.get()

        if duct_shape == "Round":
            if not round_diameter_entry.get().strip():
                clear_output()
                return
            duct_diam_in = float(round_diameter_entry.get())
            duct_diam_ft = duct_diam_in / 12
            area = pi / 4 * duct_diam_ft**2
            velocity = cfm / area
            vel_pressure = (velocity / 4005)**2 * (AIR_DENSITY / 0.075)
            reynolds = reynolds_num(AIR_DENSITY, velocity / 60, duct_diam_ft, AIR_DYN_VISC)

            if reynolds < 2000:
                friction_factor = 64 / reynolds
            else:
                friction_factor = colebrook_white_solver_fsolve(reynolds, SHEET_METAL_EPSILON, duct_diam_ft)

            pressure_drop = darcy_weisbach(friction_factor, velocity / 60, duct_diam_ft, AIR_DENSITY)

            result.set(f"Flow Area: {area:.4f} ft²\n"
                       f"Velocity: {velocity:,.1f} ft/min\n"
                       f"Pressure Drop: {pressure_drop:.4f} inWC/100 ft"
                       )
            air_properties.set(f"Air Density: {AIR_DENSITY:.4f} lbm/ft³\n"
                               f"Dynamic Viscosity: {AIR_DYN_VISC:.4f} lbm/(ft·h)\n"
                               f"Reynolds: {reynolds:,.0f}\n"
                               f"Friction Factor: {friction_factor:.4f}\n"
                               f"Velocity Pressure: {vel_pressure:.4f} inWC"
                               )


        elif duct_shape == "Rectangular":
            if not rect_width_entry.get().strip() or not rect_height_entry.get().strip():
                clear_output()
                return
            width_ft = float(rect_width_entry.get()) / 12
            height_ft = float(rect_height_entry.get()) / 12
            # Convert rectangular dimensions to an equivalent diameter.
            eq_diameter = (1.3 * (width_ft * height_ft) ** 0.625) / (width_ft + height_ft) ** 0.25
            area_eq = pi / 4 * eq_diameter**2
            velocity = cfm / area_eq
            vel_pressure = (velocity / 4005)**2 * (AIR_DENSITY / 0.075)
            reynolds = reynolds_num(AIR_DENSITY, velocity / 60, eq_diameter, AIR_DYN_VISC)

            if reynolds < 2000:
                friction_factor = 64 / reynolds
            else:
                friction_factor = colebrook_white_solver_fsolve(reynolds, SHEET_METAL_EPSILON, eq_diameter)

            pressure_drop = darcy_weisbach(friction_factor, velocity / 60, eq_diameter, AIR_DENSITY)

            result.set(f"Equiv Diam: {eq_diameter * 12:.2f} in\n"
                       f"Equiv Diam Flow Area: {area_eq:.4f} ft²\n"
                       f"Equiv Diam Velocity: {velocity:,.1f} ft/min\n"
                       f"Pressure Drop: {pressure_drop:.4f} inWC/100 ft"
                       )
            air_properties.set(f"Air Density: {AIR_DENSITY:.4f} lbm/ft³\n"
                               f"Dynamic Viscosity: {AIR_DYN_VISC:.4f} lbm/(ft·h)\n"
                               f"Reynolds: {reynolds:,.0f}\n"
                               f"Friction Factor: {friction_factor:.4f}\n"
                               f"Velocity Pressure: {vel_pressure:.4f} inWC"
                               )
        else:
            clear_output()
            return

    except ValueError:
        clear_output()
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

# GUI Setup
root = tk.Tk()
root.title("Ductulator")
root.configure(bg="#002244")  # Light navy background

style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background="#e9efff")  # Light navy background for frames
style.configure("TLabel", background="#e9efff", font=("Verdana", 14), foreground="#003366")  # Navy text
style.configure("TButton", font=("Verdana", 12, "bold"), foreground="#003366", background="#c6d2ff")
style.configure("TEntry", padding=5, relief="flat")

# Heading
heading_label = ttk.Label(root, text="Ductulator", font=("Verdana", 24, "bold"), foreground="#003366", background="#e9efff")
heading_label.grid(row=0, column=0, pady=(10, 20))

main_frame = ttk.Frame(root, padding=15)
main_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Input Section
input_frame = ttk.LabelFrame(main_frame, text="Inputs", padding=10, style="TFrame")
input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

cfm_label = ttk.Label(input_frame, text="Airflow (CFM):")
cfm_label.grid(row=0, column=0, sticky=tk.W, pady=5)
cfm_entry = ttk.Entry(input_frame)
cfm_entry.grid(row=0, column=1, pady=5)
cfm_entry.bind("<KeyRelease>", calculate)  # Real-time calculation binding

duct_shape_label = ttk.Label(input_frame, text="Duct Shape:")
duct_shape_label.grid(row=1, column=0, sticky=tk.W, pady=5)
duct_shape_var = tk.StringVar(value="Round")
duct_shape_menu = ttk.Combobox(input_frame, textvariable=duct_shape_var, values=["Round", "Rectangular"], state="readonly")
duct_shape_menu.grid(row=1, column=1, pady=5)
duct_shape_var.trace("w", update_fields)

round_diameter_label = ttk.Label(input_frame, text="Round Diameter (in):")
round_diameter_label.grid(row=2, column=0, sticky=tk.W, pady=5)
round_diameter_entry = tk.Entry(input_frame)
round_diameter_entry.grid(row=2, column=1, pady=5)
round_diameter_entry.bind("<KeyRelease>", calculate)

rect_width_label = ttk.Label(input_frame, text="Rect Width (in):")
rect_width_label.grid(row=3, column=0, sticky=tk.W, pady=5)
rect_width_entry = tk.Entry(input_frame, background="#d1d9e6", state="disabled")
rect_width_entry.grid(row=3, column=1, pady=5)
rect_width_entry.bind("<KeyRelease>", calculate)

rect_height_label = ttk.Label(input_frame, text="Rect Height (in):")
rect_height_label.grid(row=4, column=0, sticky=tk.W, pady=5)
rect_height_entry = tk.Entry(input_frame, background="#d1d9e6", state="disabled")
rect_height_entry.grid(row=4, column=1, pady=5)
rect_height_entry.bind("<KeyRelease>", calculate)

# Results Section
result_frame = ttk.LabelFrame(main_frame, text="Results", padding=10, style="TFrame")
result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

result = tk.StringVar()
result_label = ttk.Label(result_frame, textvariable=result, background="white", relief="sunken", anchor="w", padding=5, wraplength=400, font=("Verdana", 12))
result_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

air_properties = tk.StringVar()
air_properties_label = ttk.Label(result_frame, textvariable=air_properties, background="white", relief="sunken", anchor="w", padding=2, wraplength=400, font=("Verdana", 10))
air_properties_label.grid(row=1, column=0, sticky=(tk.W, tk.E))

# Footer with Author Credit
footer_label = ttk.Label(main_frame, text="Developed by Alex Kalmbach", font=("Verdana", 8), anchor="e", background="#e9efff", foreground="#003366")
footer_label.grid(row=2, column=0, sticky=(tk.E, tk.S), pady=(10, 0))

update_fields()
root.mainloop()
















