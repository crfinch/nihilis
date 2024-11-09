# src/main.py

import tcod
from engine.display_manager import DisplayManager

def main() -> None:
    """Main game entry point."""
    display_manager = DisplayManager()
    
    try:
        while True:
            # Clear all consoles
            display_manager.clear_all()
            
            # Handle events
            for event in tcod.event.wait():
                if event.type == "QUIT":
                    raise SystemExit()
                if event.type == "KEYDOWN":
                    if event.sym == tcod.event.K_ESCAPE:
                        raise SystemExit()
            
            # Draw test content with some formatting to showcase the larger font
            main_console = display_manager.get_console("main")
            if main_console:
                # Title with custom colors
                main_console.print(2, 1, "Welcome to Nihilis!", fg=(255, 223, 0))  # Gold color
                main_console.print(2, 3, "▲ Mountains", fg=(128, 128, 128))  # Gray
                main_console.print(2, 4, "≈ Rivers", fg=(0, 148, 255))  # Blue
                main_console.print(2, 5, "♠ Forests", fg=(0, 255, 0))  # Green
                
            status_console = display_manager.get_console("status")
            if status_console:
                status_console.print(1, 1, "Status: Active", fg=(0, 255, 0))
                status_console.print(status_console.width - 20, 1, "HP: 100/100", fg=(255, 0, 0))
                
            minimap_console = display_manager.get_console("minimap")
            if minimap_console:
                minimap_console.draw_frame(
                    0, 0, 
                    minimap_console.width, 
                    minimap_console.height,
                    title=" World Map "
                )
                # Add some sample terrain markers
                minimap_console.print(5, 5, "▲", fg=(128, 128, 128))
                minimap_console.print(7, 7, "≈", fg=(0, 148, 255))
                minimap_console.print(9, 6, "♠", fg=(0, 255, 0))
                
            message_console = display_manager.get_console("message_log")
            if message_console:
                message_console.draw_frame(
                    0, 0,
                    message_console.width,
                    message_console.height,
                    title=" Messages "
                )
                # Add some sample messages with different colors
                message_console.print(2, 2, "You enter the region.", fg=(255, 255, 255))
                message_console.print(2, 3, "You see mountains ahead.", fg=(192, 192, 192))
                message_console.print(2, 4, "A cool breeze blows.", fg=(128, 192, 255))
            
            # Render everything to the screen
            display_manager.render()
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        display_manager.close()

if __name__ == "__main__":
    main()