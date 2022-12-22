# Python Powered Arcade Style Shooting Gallery
import pygame
import math

  # Setup values
pygame.init()
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font('assets/font/myFont.ttf', 32)
big_font = pygame.font.Font('assets/font/myFont.ttf', 60)
pygame.mouse.set_cursor(*pygame.cursors.broken_x)
WIDTH = 900
HEIGHT = 800
screen = pygame.display.set_mode([WIDTH, HEIGHT])
bgs = []
banners = []
guns = []
target_images = [[],[],[]]  # List of lists as each level has 3 targets
targets = {1: [10, 5, 3],  # Number of each target type in each level
           2: [12, 8, 5],
           3: [15, 12, 8, 3]}
level = 0
points = 0
total_shots = 0
ammo = 0
counter = 1
time_passed = 0
time_remaining = 60
menu = True
game_over = False
pause = False
clicked = False
write_values = False
new_coords = True
one_coords = [[],[],[]]
two_coords = [[],[],[]]
three_coords = [[],[],[]]
menu_img = pygame.image.load(f'assets/menus/mainMenu.png')
game_over_img = pygame.image.load(f'assets/menus/gameOver.png')
pause_img = pygame.image.load(f'assets/menus/pause.png')
mode = 2  # 0 = freeplay, 1 = accuracy, 2 = timed
mode_type = ['Freeplay Mode', 'Accuracy Mode', 'Timed Mode']
best_freeplay = 50
best_ammo = 0
best_timed = 0
shot = False

  # Get backgrounds, banners, guns and targets for each level
for i in range(1,4):  # For levels 1-3
    bgs.append(pygame.image.load(f'assets/bgs/{i}.png'))  # Get backgrounds in the above range
    banners.append(pygame.image.load(f'assets/banners/{i}.png'))  # Get banners
    guns.append(pygame.transform.scale(pygame.image.load(f'assets/guns/{i}.png'), (200, 200)))  # Get guns
    if i < 3:  # For levels 1 & 2 as level 3 has more target types
        for j in range(1, 4):
            target_images[i - 1].append(pygame.transform.scale(
                pygame.image.load(f'assets/targets/{i}/{j}.png'), (120 - (j*18), 80 - (j*12))))  # Load the targets for each level & scale them smaller as level increases
    else:  # Basically the same but increased range of j to include extra target on last level
        for j in range(1, 5):
            target_images[i - 1].append(pygame.transform.scale(
                pygame.image.load(f'assets/targets/{i}/{j}.png'), (120 - (j*18), 80 - (j*12))))  # Load the targets for each level & scale them smaller as level increases

  # Read existing high scores from text file
file = open('high_scores.txt', 'r')
read_file = file.readlines()
file.close()
  # Import high scores into the game
best_freeplay = int(read_file[0])
best_ammo = int(read_file[1])
best_timed = int(read_file[2])

  # Adding music
pygame.mixer.init()
pygame.mixer.music.load('assets/sounds/Background music.wav')
pygame.mixer.music.play()

  # Adding sound effects
bird_sound = pygame.mixer.Sound('assets/sounds/Drill Gear.wav')
bird_sound.set_volume(.4)
plate_sound = pygame.mixer.Sound('assets/sounds/Broken plates.wav')
plate_sound.set_volume(.5)
laser_sound = pygame.mixer.Sound('assets/sounds/Laser Gun.wav')
# laser_sound.set_volume(.8)

  # Display the score, time, shots & ammo on the screen
def draw_score():
    level_color = ['crimson', 'blue', 'purple']
    mode_text = font.render(f'{mode_type[mode]}', True, level_color[level - 1])
    points_text = font.render(f'Points: {points}', True, level_color[level - 1])  # Display the score in the color of the level
    shots_text = font.render(f'Total shots: {total_shots}', True, level_color[level - 1])
    time_text = font.render(f'Time elapsed: {time_passed} s', True, level_color[level - 1])
    screen.blit(mode_text, (0, 565))
    if mode == 0:
        screen.blit(points_text, (320, 665))  # Points
        screen.blit(shots_text, (320, 700))  # Total shots
        screen.blit(time_text, (320, 735))  # Time
    elif mode == 1:  # Add ammo on accuracy mode
        ammo_text = font.render(f'Ammo remaining: {ammo}', True, level_color[level - 1])
        screen.blit(points_text, (320, 660))
        screen.blit(shots_text, (320, 687))
        screen.blit(time_text, (320, 714))
        screen.blit(ammo_text, (320, 741))  # Ammo remaining
    elif mode == 2:  # Add time on timed mode
        timed_text = font.render(f'Time remaining: {time_remaining} s', True, level_color[level - 1])
        screen.blit(points_text, (320, 660))
        screen.blit(shots_text, (320, 687))
        screen.blit(time_text, (320, 714))
        screen.blit(timed_text, (320, 741))  # Time remaining

  # Display the gun on the screen
def draw_gun():
    mouse_pos = pygame.mouse.get_pos()  # mouse_pos[0] = X axis, [1] = Y axis
    gun_point = (WIDTH/2, HEIGHT - 200)  # Centre the gun at the top-centre of the banner
    lasers = ['red', 'cyan', 'magenta']
    clicks = pygame.mouse.get_pressed()
    
      # Find slope from gun to mouse (unless mouse is directly above gun to avoid dividing by 0)
    if mouse_pos[0] != gun_point[0]:
        slope = (mouse_pos[1] - gun_point[1]) / (mouse_pos[0] - gun_point[0])
    else:
        slope = -100000  # Make slope vertical if mouse is directly above gun)
      
      # Set the gun rotation based on slope
    angle = math.atan(slope)  # Angle = inverse tan (atan) of the slope
    rotation = math.degrees(angle)  # Convert from radians to degrees

      # Set the gun position and rotation
    if mouse_pos[0] < WIDTH/2:  # While the mouse is on the left of the screen
        gun = pygame.transform.flip(guns[level - 1], True, False)  # Flip the gun in X but not Y axis
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 90 - rotation), (WIDTH/2 - 90, HEIGHT - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 10)  # Show shots on the screen
    else:  # While the mouse is on the right of the screen
        gun = guns[level - 1]
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 270 - rotation), (WIDTH/2 - 30, HEIGHT - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 10)  # Show shots on the screen

  # Move the targets, different speeds for each target type
def move_level(coords):
    if level == 1 or level == 2:  # Set the maximum speed level, extra level for level 3
        max_val = 3
    else:
        max_val = 4
    for i in range(max_val):
        for j in range(len(coords[i])):
            my_coords = coords[i][j]
            if my_coords[0] < -150:
                coords[i][j] = (WIDTH, my_coords[1])  # When the target is fully off the screen, move it to the other side while keeping the same height
            else:
                coords[i][j] = (my_coords[0] - 2**i, my_coords[1])  # While on screen, move the targets to the left at a speed of 2^target_level (higher level targets move exponentially faster)
    return coords

  # Draw the level & display targets on the screen
def draw_level(coords):
    if level == 1 or level == 2:  # For levels 1 & 2 as 3 has more target types
        target_rects = [[], [], []]  # Make invisible hit box squares on the targets
    else:
        target_rects = [[], [], [], []]  # Same with extra list for the additional target type
    
      # Get a list of coordinates for where we want the targets to spawn
    for i in range(len(coords)):
        for j in range(len(coords[i])):
            target_rects[i].append(pygame.rect.Rect((coords[i][j][0] + 20, coords[i][j][1]),  # Set the X & Y coordinates of the hit box
                (60 - i * 12, 60 - i * 12)))  # Set the hit box size & decrease size as level increases
            screen.blit(target_images[level-1][i], coords[i][j])  # Draw the targets at these coordinates
    return target_rects

  # Track the score (based on the number of coordinates being used for targets) & remove the coordinates once hit
def check_shot(targets, coords):
    global points
    mouse_pos = pygame.mouse.get_pos()
    for i in range(len(targets)):
        for j in range(len(targets[i])):
            if targets[i][j].collidepoint(mouse_pos):
                coords[i].pop(j)  # If the target overlaps the mouse position then "pop" the target's coordinates out of the list
                points += 10 + 10 * (i**2)  # Give points, more points for higher target levels
                  # Make the appropriate sound effect when target is hit
                if level == 1:
                    bird_sound.play()
                elif level == 2:
                    plate_sound.play()
                elif level == 3:
                    laser_sound.play()

    return coords

  # Draw the main menu screen
def draw_menu():
    global game_over, pause, mode, level, menu, time_passed, total_shots, points, ammo, clicked
    global time_remaining, best_freeplay, best_ammo, best_timed, write_values, new_coords
    game_over = False
    pause = False
    screen.blit(menu_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()

      # Draw the button rectangles over the menu screen to register clicks
    freeplay_button = pygame.rect.Rect((170, 524), (260, 100))
    ammo_button = pygame.rect.Rect((475, 524), (260, 100))
    clicks = pygame.mouse.get_pressed()
    timed_button = pygame.rect.Rect((170, 661), (260, 100))
    reset_button = pygame.rect.Rect((475, 661), (260, 100))

      # Display high scores
    screen.blit(font.render(f'{best_freeplay} s', True, 'slateblue'), (340, 581))
    screen.blit(font.render(f'{best_ammo}', True, 'slateblue'), (650, 581))
    screen.blit(font.render(f'{best_timed}', True, 'slateblue'), (350, 711))

      # Register button clicks
        # Freeplay button
    if freeplay_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 0
        level = 1
        menu = False
        time_passed = 0
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True

        # Ammo button
    if ammo_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 1
        level = 1
        menu = False
        time_passed = 0
        total_shots = 0
        points = 0
        ammo = 85  # There are 81 targets
        clicked = True
        new_coords = True

        # Timed button
    if timed_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 2
        level = 1
        menu = False
        time_passed = 0
        total_shots = 0
        points = 0
        time_remaining = 45
        clicked = True
        new_coords = True

        # Reset button
    if reset_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        best_freeplay = 0
        best_ammo = 0
        best_timed = 0
        write_values = True
        clicked = True

  # Draw the game over screen
def draw_game_over():
    global clicked, level, pause, game_over, menu, points
    global total_shots, time_passed, time_remaining
    if mode == 0:  # Score is end time for freeplay & points for accuracy & timed
        display_score = str(time_passed) + ' s'
    else:
        display_score = points

    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    exit_button = pygame.rect.Rect((170, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100))

    screen.blit(game_over_img, (0, 0))
    screen.blit(big_font.render(f'{display_score}', True, 'slateblue'), (650, 570))
    
      # Back to main menu button
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        level = 0
        pause = False
        game_over = False
        menu = True
        points = 0
        total_shots = 0
        time_passed = 0
        time_remaining = 0

      # End game button
    if exit_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        global run
        run = False

  # Draw the pause screen
def draw_pause():
    global level, pause, menu, total_shots, time_passed, time_remaining, clicked, new_coords
    screen.blit(pause_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    resume_button = pygame.rect.Rect((170, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100))

      # Resume game
    if resume_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        level = resume_level
        pause = False
        clicked = True

      # Return to menu
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        level = 0
        pause = False
        menu = True
        total_shots = 0
        time_passed = 0
        time_remaining = 0
        clicked = True
        new_coords = True
        pygame.mixer.music.play()  # Start music when you go to the main menu

################################################################################################################################################################
################################################################################################################################################################

  # Main game loop
run = True
while run:
    timer.tick(fps)  # Make timer tick at set frame rate
    if level != 0:
        if counter < 60:
            counter += 1
        else:
            counter = 1
            time_passed += 1
            if mode == 2:
                time_remaining -= 1

    if new_coords:
          # Initialise target coordinates
        one_coords = [[],[],[]]
        two_coords = [[],[],[]]
        three_coords = [[],[],[],[]]

          # Set target coordinates
        for i in range(3):  #Level 1
            my_list = targets[1]  # Use the list for number of each target from the "targets" list of lists
            for j in range(my_list[i]):
                one_coords[i].append((WIDTH//(my_list[i]) * j,  # Evenly spread the targets across the X axis
                    300 - (i * 150) + 30 * (j%2)))  # Set the position of each target type in the Y axis, alternating each by 30
                    
        for i in range(3):  # Level 2
            my_list = targets[2]
            for j in range(my_list[i]):
                two_coords[i].append((WIDTH//(my_list[i]) * j,
                    300 - (i * 150) + 30 * (j%2)))

        for i in range(4):  # Level 3, increased range for the extra target type
            my_list = targets[3]
            for j in range(my_list[i]):
                three_coords[i].append((WIDTH//(my_list[i]) * j,
                    300 - (i * 100) + 30 * (j%2)))
        
        new_coords = False
        

    screen.fill('black')  # Default black background
    screen.blit(bgs[level - 1], (0, 0))  # Display level background at (0, 0) - level 1 = bgs[0]
    screen.blit(banners[level - 1], (0, HEIGHT - 200))  # Display banners (banner is 200px in HEIGHT)
    
    if menu:
        level = 0
        draw_menu()
    if game_over:
        level = 0
        draw_game_over()
    if pause:
        level = 0
        draw_pause()

      # Display the targets for each level, move them and react to being shot
    if level == 1:
        target_boxes = draw_level(one_coords)
        one_coords = move_level(one_coords)
        if shot:
            one_coords = check_shot(target_boxes, one_coords)
            shot = False  # End the loop after 1 run & prevent "long click and drag" style shooting
    elif level == 2:
        target_boxes = draw_level(two_coords)
        two_coords = move_level(two_coords)
        if shot:
            two_coords = check_shot(target_boxes, two_coords)
            shot = False
    elif level == 3:
        target_boxes = draw_level(three_coords)
        three_coords = move_level(three_coords)
        if shot:
            three_coords = check_shot(target_boxes, three_coords)
            shot = False

      # Display the gun & score on the game screen (level 0 = title screen)
    if level > 0:
        draw_gun()
        draw_score()
      
      # Close the loop & end the game when user closes the window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # If the mouse is clicked & clicked with the left "event.button"
            mouse_position = pygame.mouse.get_pos()
            if (0 < mouse_position[0] < WIDTH) and (0 < mouse_position[1] < HEIGHT - 200):  # If the mouse is on the game window (excluding the banner)
                shot = True
                total_shots += 1  # Track number of shots
                if mode == 1:
                    ammo -= 1  # Reduce ammo on "accuracy mode"
        
              # Pause from game screen
            if (670 < mouse_position[0] < 860) and (660 < mouse_position[1] < 715):  # If the mouse is on the pause button
                resume_level = level  # Save what level the game paused on
                pause = True
                clicked = True
        
              # Go back to main menu from the game screen
            if (670 < mouse_position[0] < 860) and (715 < mouse_position[1] < 760):  # If the mouse is on the reset button
                menu = True
                clicked = True
                new_coords = True
                pygame.mixer.music.play()  # Start music when you go to the main menu


        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and clicked:
            clicked = False  # Set clicked to false when the left mouse button is released

      # Move to the next level & end game
    if level > 0:
        if target_boxes == [[],[],[]] and level < 3:  # When there are no more targets in levels 1 & 2, move to the next level
            level += 1

          # Game over conditions
        if (level == 3 and target_boxes == [[],[],[],[]]) or (mode == 1 and ammo == 0) or (mode == 2 and time_remaining == 0):
            new_coords = True
            pygame.mixer.music.play()  # Start music when you go to the main menu
              # Save any new high scores
            if mode == 0:  # Freeplay score
                if best_freeplay > time_passed or best_freeplay == 0:
                    best_freeplay = time_passed
                    write_values = True
            if mode == 1:  # Accuracy score
                if best_ammo < points:
                    best_ammo = points
                    write_values = True
            if mode == 2:  # Timed score
                if best_timed < points:
                    best_timed = points
                    write_values = True

            game_over = True

      # Save the new high scores outside the game
    if write_values:
        file = open('high_scores.txt', 'w')
        file.write(f'{best_freeplay}\n{best_ammo}\n{best_timed}')
        file.close
        write_values = False


    pygame.display.flip()
pygame.quit()  # Close the program