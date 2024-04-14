from DatabaseManager import DBManager
import random
import time
from ClearScreen import clear_screen


class Fitness:
    @staticmethod
    def get_stats(email):
        """ Fetches or initializes stats for the given email. """
        with DBManager.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM health_statistics WHERE email = %s", (email,))
            stats = cursor.fetchone()

            # member stats
            if stats:
                print("Your stats:")
                print("| {:<15} | {:^10} |".format("Metric", "Value"))
                for key, value in stats.items():
                    print("| {:<15} | {:^10} |".format(key.capitalize(), value))
            else:
                if email == "guest":
                    # Guest handling: initialize stats
                    print("To personalize your guest experience, please answer the following questions:")
                    print("What is your fitness level?\n1. Beginner\n2. Intermediate\n3. Advanced")
                    choice = int(input("Enter choice (1-3): "))
                    range_start, range_end = {1: (1, 3), 2: (4, 7), 3: (8, 10)}.get(choice, (1, 3))
                    stats = {
                        'fitness_level': choice,
                        'strength': random.randint(range_start, range_end),
                        'flexibility': random.randint(range_start, range_end),
                        'endurance': random.randint(range_start, range_end),
                        'stamina': random.randint(range_start, range_end),
                        'has_water': random.choice([True, False]),
                        'has_protein': random.choice([True, False, False, False]),
                        'is_injured': False
                    }
                    cursor.execute("""
                        INSERT INTO health_statistics (email, fitness_level, strength, flexibility, endurance, stamina, has_water, has_protein, is_injured)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (email, choice, *stats.values()))
                    print("Your guest stats have been initialized.")
                else:
                    print("You must be a new member - you don't have any stats yet.")
                    Fitness.setup_stats(cursor, email)
            conn.commit()

    @staticmethod
    def setup_stats(cursor, email):
        """ Prompts the member to set up their stats. """
        print("Let's set up your fitness stats.")
        fitness_level = int(input("What is your fitness level?\n1. Beginner\n2. Intermediate\n3. Advanced\nEnter choice (1-3): "))
        range_start, range_end = {1: (1, 3), 2: (4, 7), 3: (8, 10)}.get(fitness_level, (1, 3))
        stats = {
            'fitness_level': fitness_level,
            'strength': random.randint(range_start, range_end),
            'flexibility': random.randint(range_start, range_end),
            'endurance': random.randint(range_start, range_end),
            'stamina': random.randint(range_start, range_end),
            'has_water': random.choice([True, False]),
            'has_protein': random.choice([True, False, False, False]),
            'is_injured': False
        }
        cursor.execute("""
            INSERT INTO health_statistics (email, fitness_level, strength, flexibility, endurance, stamina, has_water, has_protein, is_injured)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (email, fitness_level, *stats.values()))
        print("Your stats have been initialized.")

    @staticmethod
    def animation():
        figure = 'ᕕ( ᐛ )ᕗ'
        trail = ' ε='
        total_duration = 2
        frame_duration = 0.2
        iterations = int(total_duration / frame_duration)

        for _ in range(iterations):
            clear_screen()
            print("Working out...\n")
            print(trail + figure)
            trail += ' ε='
            time.sleep(frame_duration)
     
        
    @staticmethod
    def go_to_gym(email):
        clear_screen()
        with DBManager.connection() as conn:
            cursor = conn.cursor()

            if email.lower() == "guest":
                print("Welcome to Pain to Progress Health and Fitness Club, Guest!")
                Fitness.get_stats("guest")
            else:
                cursor.execute("SELECT name FROM member_accounts WHERE email = %s", (email,))
                name = cursor.fetchone()
                if not name:
                    print("No member found with this email. Please register or check your email.")
                    return
                print(f"Welcome back to Pain to Progress Health and Fitness Club, {name['name']}!")
                Fitness.get_stats(email)  # Get stats for registered members

            Fitness.navigate_gym(cursor, email)

    def navigate_gym(cursor, email):
        # Fetch available rooms that are not occupied
        cursor.execute("SELECT room_id, room_name FROM rooms WHERE room_availability = TRUE")
        rooms = {room['room_id']: room['room_name'] for room in cursor.fetchall()}
        if not rooms:
            print("Currently, no rooms are available. Please try again later.")
            return

        while True:
            print("----------------------------------------------------")
            print("Where would you like to go?")
            for room_id, room_name in rooms.items():
                print(f"{room_id}. {room_name}")

            choice = input("\nEnter the number of the room you'd like to visit: ")
            try:
                chosen_room_id = int(choice)
                if chosen_room_id not in rooms:
                    print("Invalid room number. Please choose a valid number.")
                    continue

                # Fetch equipment in the selected room
                cursor.execute("""
                    SELECT equipment_id, equipment_name, quality
                    FROM equipment
                    WHERE room_id = %s AND quality > 0
                    ORDER BY equipment_id
                """, (chosen_room_id,))
                equipment = cursor.fetchall()

                if not equipment:
                    print(f"No equipment available in {rooms[chosen_room_id]}. Choose another room.")
                    continue

                print(f"\nIn the {rooms[chosen_room_id]}, you can use the following equipment:")
                equipment_list = {index + 1: (equip['equipment_id'], equip['quality'], equip['equipment_name']) for index, equip in enumerate(equipment)}
                for index, (equip_id, equip_quality, equip_name) in equipment_list.items():
                    print(f"{index}. {equip_name} (Quality: {equip_quality})")

                equip_choice = int(input("\nEnter the number of the equipment you'd like to use: "))
                if equip_choice in equipment_list:
                    chosen_equip_id, equip_quality, chosen_equipment_name = equipment_list[equip_choice]
                    print(f"\nYou are now using the {chosen_equipment_name}. Enjoy your workout!")

                    if equip_quality < 3:
                        print("Warning: Equipment has very low quality, increased chance of getting injured!")
                        if random.randint(1, 10) > 1:  # 90% chance of injury
                            print("You have been injured due to the poor quality of the equipment!")
                            Fitness.handle_injury(cursor, email)
                            input("Press Enter to leave the gym...")
                            return
                    
                    Fitness.animation()
                    Fitness.change_stats(cursor, email, chosen_equip_id, equip_quality)
                else:
                    print("Invalid equipment number. Please choose a valid number.")
            except ValueError:
                print("Please enter a valid number.")

    @staticmethod
    def change_stats(cursor, email, equip_id, quality):
        # Decrease equipment quality and handle user stats
        cursor.execute("UPDATE equipment SET quality = GREATEST(1, quality - 2) WHERE equipment_id = %s;", (equip_id,))
        cursor.connection.commit()

        # Fetch and update user stats
        cursor.execute("SELECT fitness_level, strength, flexibility, endurance, stamina, has_water, has_protein, is_injured FROM health_statistics WHERE email = %s", (email,))
        stats = cursor.fetchone()

        if stats:
            # Decide randomly whether to improve a stat
            improve = random.choice([True, False])  # 50% chance to improve or not improve
            if improve:
                # Randomly increase one stat, decrease stamina
                improved_stat = random.choice(['fitness_level', 'strength', 'flexibility', 'endurance'])
                if stats[improved_stat] < 10:
                    new_value = stats[improved_stat] + 1
                    cursor.execute(f"UPDATE health_statistics SET {improved_stat} = %s WHERE email = %s", (new_value, email))
                    print(f"Your {improved_stat} has improved to {new_value}.")
                else:
                    print("Your stats are already at their maximum values. No improvements this session.")
            else:
                print("No improvements in your stats this session.")

            # Always decrease stamina
            new_stamina = max(0, stats['stamina'] - 2)
            cursor.execute("UPDATE health_statistics SET stamina = %s WHERE email = %s", (new_stamina, email))
            cursor.connection.commit()
            Fitness.print_mood()
            print("----------------------------------------------------")
            print(f"Stamina is now {new_stamina}.")

            # Re-fetch and show all stats to reflect changes
            cursor.execute("SELECT * FROM health_statistics WHERE email = %s", (email,))
            updated_stats = cursor.fetchone()
            print("Updated stats after your workout:")
            print("| {:<15} | {:^7} |".format("Metric", "Value"))
            for key, value in updated_stats.items():
                print("| {:<15} | {:^7} |".format(key.capitalize(), value))

            # Check if stamina is 0, then prompt user to leave the gym
            if new_stamina == 0:
                print("Your stamina has dropped to zero, you can't go on.")
                print("Please rest and recover before returning to the gym.")
                input("Press Enter to leave the gym...")

        else:
            print("No stats found. Unable to update.")

    def reset_stamina(cursor, email):
        """Resets the member's stamina based on their fitness level."""
        # Fetch the current fitness level of the member
        cursor.execute("SELECT fitness_level FROM health_statistics WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result:
            fitness_level = result['fitness_level']

            # Determine new stamina based on fitness level
            if fitness_level == 1:  # Beginner
                new_stamina = 5
            elif fitness_level == 2:  # Intermediate
                new_stamina = 7
            elif fitness_level == 3:  # Advanced
                new_stamina = 10
            else:
                new_stamina = 5  # Default case if fitness level is undefined

            # Update the stamina in the database
            cursor.execute("UPDATE health_statistics SET stamina = %s WHERE email = %s", (new_stamina, email))
            cursor.connection.commit()
            print(f"Stamina reset to {new_stamina} based on fitness level {fitness_level}.")
        else:
            print("Failed to fetch fitness level; stamina not reset.")


    @staticmethod
    def handle_injury(cursor, email):
        ...
        # Reduce all stats due to injury
        cursor.execute("""
            UPDATE health_statistics 
            SET is_injured = TRUE, fitness_level = GREATEST(1, fitness_level - 1), strength = GREATEST(1, strength - 1),
            flexibility = GREATEST(1, flexibility - 1), endurance = GREATEST(1, endurance - 1), stamina = 0
            WHERE email = %s
        """, (email,))
        cursor.connection.commit()

        # Fetch updated stats after injury
        cursor.execute("SELECT * FROM health_statistics WHERE email = %s", (email,))
        updated_stats = cursor.fetchone()

        print("Due to an injury, all your stats have been reduced and stamina set to 0.")
        Fitness.print_updated_stats(updated_stats)
        Fitness.reset_stamina(cursor, email)  # Reset stamina based on fitness level after handling injury
        print("Please rest and recover before returning to the gym.")
        input("Press Enter to leave the gym...")
        
    @staticmethod
    def print_updated_stats(updated_stats):
        if updated_stats:
            print("Updated stats after your activity:")
            print("| {:<15} | {:^7} |".format("Metric", "Value"))
            for key, value in updated_stats.items():
                print("| {:<15} | {:^7} |".format(key.capitalize(), value))
        else:
            print("No stats found after update.")


    def print_mood():
        positive_sentences = [
            "Congratulations on completing your workout! You feel invigorated and ready for your next challenge.",
            "Well done! You emerge from your workout feeling stronger and more resilient.",
            "A valiant effort! You sense a surge of energy coursing through your veins as you finish your workout.",
            "Impressive! You feel a sense of accomplishment wash over you as you catch your breath after your intense workout.",
            "Phew! That was quite the workout. You're feeling fatigued, but also satisfied with your progress.",
            "You've really pushed your limits today! Despite feeling exhausted, you know that every drop of sweat was worth it.",
            "Bravo! You feel a sense of pride as you reflect on the intensity of your workout and the gains you've made.",
            "That was a challenging session, but you powered through! You're a true warrior of the gym.",
            "Impressive display! You're filled with a sense of vigor and enthusiasm for your fitness journey."
            "Outstanding dedication! You're basking in the glow of success and personal growth."
        ]

        negative_sentences = [
            "Yikes! That workout really took a toll on you. You feel drained and fatigued.",
            "Uh oh... You may have overexerted yourself. Your muscles ache, and you feel utterly exhausted.",
            "Ouch... You're definitely feeling the consequences of pushing too hard. Everything hurts.",
            "That workout was a struggle from start to finish. You feel weak and defeated.",
            "Disappointing... You couldn't quite keep up with the intensity of the workout. You're left feeling frustrated.",
            "Well, that didn't go as planned. You're left feeling discouraged and demoralized by the difficulty of the workout.",
            "That was rough... You feel battered and bruised, both physically and mentally.",
            "You've hit a wall. Your energy is depleted, and you're left wondering if it was worth it.",
            "Not your best performance. You feel disheartened by your lack of progress during the workout.",
            "A total disaster... You're left questioning your abilities and wondering if you'll ever improve."
        ]

        all_sentences = positive_sentences + negative_sentences
        print(random.choice(all_sentences))


        