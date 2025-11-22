import dearpygui.dearpygui as dpg

dpg.create_context()

# Create viewport first
dpg.create_viewport(title='Minimal Test', width=800, height=600)
dpg.setup_dearpygui()

# Create a simple window
with dpg.window(label="Test Window", width=700, height=500, pos=(50, 50)):
    dpg.add_text("If you can see this text, DearPyGui is working!")
    dpg.add_button(label="Click Me", callback=lambda: print("Button clicked!"))
    dpg.add_input_text(label="Type here", default_value="Test input")

# Show and run
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
