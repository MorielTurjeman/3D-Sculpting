import dearpygui.dearpygui as dpg


dpg.create_context()

with dpg.window(id="Primary Window", label="Example Window"):
    dpg.add_text("Hello, world")
    dpg.add_button(label="Save")
    dpg.add_input_text(label="string", default_value="Quick brown fox")
    dpg.add_slider_float(label="float", default_value=0.273, max_value=1)
dpg.set_primary_window("Primary Window", False)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()