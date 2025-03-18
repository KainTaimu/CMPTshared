# -------------------------------
# Erwin Panergo, Hadi Moughnieh
# Programming Project - Milestone#1
# -------------------------------


def print_menu() -> None:
    """
    purpose:
    parameter:
    return:
    """
    print("""
Edmonton Transit System
---------------------------------
(1) Load route data
(2) Load shapes data
(3) Reserved for future use

(4) Print shape IDs for a route
(5) Print coordinates for a shape ID
(6) Reserved for future use

(7) Save routes and shapes in a pickle
(8) Load routes and shapes from a pickle

(9) Reserved for future use
(0) Quit
""")
    

def main() -> None:
    """
    purpose:
    parameter:
    return:
    """
    
    running = True
    while running:
        print_menu()
        user_input = input("Enter Command: ").strip()
        if user_input == "0":
            running = False
        elif user_input == "1":
            pass
        elif user_input == "2":
            pass
        elif user_input == "3":
            pass
        elif user_input == "4":
            pass
        elif user_input == "5":
            pass
        elif user_input == "6":
            pass
        elif user_input == "7":
            pass
        elif user_input == "8":
            pass
        elif user_input == "9":
            pass
        else:
            print("Invalid Option")

    
if __name__ == "__main__":
    main()