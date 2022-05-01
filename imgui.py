from cProfile import label
from tkinter import Button
import dearpygui.dearpygui as dpg

dpg.create_context()

def button_callback(sender, app_data, user_data):
    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user data is:{user_data}")


with dpg.window(label="first test") as window1:
    b0=dpg.add_button(label="PressMe1")
    b1=dpg.add_button(label="pressMe2")
    dpg.add_button(label="Apply", callback=button_callback, user_data="some data")

    btn=dpg.add_button(label="Apply2", )
    dpg.set_item_callback(btn, button_callback)
    dpg.set_item_user_data(btn, "somme extra User data")

    slider_int=dpg.add_slider_int(label="slide to left", width=100)
    slider_float=dpg.add_slider_float(label="slide to right", width=100)

print(f"Printing item tag's: {window1}, {b0},{b1},{slider_int}, {slider_float}")

B2=dpg.add_button(label="Me Too!!", parent=window1)
dpg.create_viewport(title='Custom Title', width=600, height=300)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
