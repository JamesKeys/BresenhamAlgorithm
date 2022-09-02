try:
	import cv2
except:
	print("OpenCV is not installed or could not be imported properly.\n Check your packages then try again")
	quit()

import numpy as np
import math


def main():
	# create window to be used for displaying the available controls
	launch_controls_window()

	# initialize variables for the main grid
	window_name = "grid"
	window_width = 1000
	window_height = 500
	grid_size = 50
	orig_grid = initGrid(window_width, window_height, grid_size)

	# initialize variables for the zoomed in view of the grid
	zoom_window_name = "zoom"
	zoom_grid_size = 125
	zoom_window_width = zoom_grid_size*3
	zoom_window_height = zoom_grid_size*3
	orig_zoom_grid = initGrid(zoom_window_width, zoom_window_height, zoom_grid_size)
	fillXY(orig_zoom_grid, 0, 0, zoom_window_width, zoom_window_height, zoom_grid_size)

	# create variables for the points and calculate pixels to be filled in using Bresenham's Algorithm
	pointA = [0,0]
	pointB = [10,5]
	ePress = 1
	slope = pointB[1]/pointB[0]
	pixels = bresenham(pointA[0], pointA[1], pointB[0], pointB[1])

	# find locations to put the threshold circle depending on the slope of the line
	threshX, threshY = convertCoords(1 if pointB[0] >= pointB[1] else 0.5, 0.5 if pointB[0] >= pointB[1] else 1,zoom_window_width, zoom_window_height, zoom_grid_size)

	# create the two OpenCV windows using window height, width, and grid size to use
	initWindow(window_name, window_width, window_height, grid_size)
	initWindow(zoom_window_name, zoom_window_width, zoom_window_height, zoom_grid_size)

	# save a copy of the original grid to be loaded when the second pixel changes location (saves time recalculating background)
	grid = orig_grid.copy()
	grid = initPoints(grid, pointA, pointB, window_width, window_height, grid_size)
	
	zoom_grid = orig_zoom_grid.copy()

	# display the starting windows
	cv2.imshow(window_name, grid)
	cv2.imshow(zoom_window_name, zoom_grid)
	
	key = cv2.waitKey()
	# while the user has not quit and we have not reached the second point...
	while key != ord('q') and ePress//2 < max(pointB[0], pointB[1]):

		# if the user wants to move the second point
		if key in [ord('w'), ord('a'), ord('s'), ord('d')]:

			# move the point accordingly
			if key == ord('w'):
				pointB[1] += 1
			elif key == ord('a'):
				pointB[0] -= 1
			elif key == ord('s'):
				pointB[1] -= 1
			elif key == ord('d'):
				pointB[0] += 1
	
			# reset variables
			slope = pointB[1]/pointB[0]
			ePress = 1
			grid = orig_grid.copy()
			zoom_grid = orig_zoom_grid.copy()
			pixels = bresenham(pointA[0], pointA[1], pointB[0], pointB[1])
			threshX, threshY = convertCoords(1 if pointB[0] >= pointB[1] else 0.5, 0.5 if pointB[0] >= pointB[1] else 1,zoom_window_width, zoom_window_height, zoom_grid_size)

			# reset circles
			grid = initPoints(grid, pointA, pointB, window_width, window_height, grid_size)

			# re-show updated image
			cv2.imshow(window_name, grid)

		# move forward with step of Bresenham Algorithm
		if key == ord("e"):
			ePress += 1

			# if the slope is < 1
			if pointB[0] >= pointB[1]:
				curr_x = ePress//2
				
				# if this is a new X to look at, show pre-filled pixel and values
				if ePress % 2 == 0:
					# reset the zoomed in grid back to beginning
					zoom_grid = orig_zoom_grid.copy()
					cv2.circle(zoom_grid, (threshX, threshY), 2, (255,255,255), 3)

					# calculate the offset to use for the zoomed in view
					curr_y = slope*(curr_x-1) % 1
					if curr_y > 0.5:
						curr_y -= 1

					# create the line for the zoomed in view of the grid and find the coordinates to display information
					zoom_start_line = convertCoords(-1, -1*slope+curr_y, zoom_window_width, zoom_window_height, zoom_grid_size)
					zoom_end_line = convertCoords(2, 2*slope+curr_y, zoom_window_width, zoom_window_height, zoom_grid_size)
					text_coords = convertCoords(-0.9, 1.9, zoom_window_width, zoom_window_height, zoom_grid_size)
					
					cv2.line(zoom_grid,zoom_start_line, zoom_end_line, (255,255,255), 1)
					cv2.rectangle(zoom_grid, text_coords, (text_coords[0]+math.floor(1.4*zoom_grid_size), text_coords[1]+140), (55,55,55), -1)

					# display current information on Bresenham's Algorithm variables
					cv2.putText(zoom_grid, f"2dx: {pointB[0]*2}", (text_coords[0]+5, text_coords[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, f"2dy: {pointB[1]*2}", (text_coords[0]+5, text_coords[1]+45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, f"d_hat: {pixels[curr_x-1]['d_hat']}", (text_coords[0]+5, text_coords[1]+75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, "d_hat +=2dy" if pixels[curr_x-1]['d_hat'] <= 0 else "d_hat +=(2dy-2dx)", (text_coords[0]+5, text_coords[1]+105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, "Increment y? NO" if pixels[curr_x-1]['d_hat'] <= 0 else "Increment y? YES", (text_coords[0]+5, text_coords[1]+135), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

				# After the user has seen and understood the next step, show the pixel which will actually be filled in
				else:
					# fill in the pixel on both windows
					fillXY(grid, pixels[curr_x]["x"], pixels[curr_x]["y"], window_width, window_height, grid_size)
					fillXY(zoom_grid, 1, 0 if(pixels[curr_x]["y"] == pixels[curr_x-1]["y"]) else 1, zoom_window_width, zoom_window_height, zoom_grid_size)

					# re-fill in the line, circle, and text box because the filled in box overwrote the pixel values
					cv2.line(zoom_grid,zoom_start_line, zoom_end_line, (255,255,255), 1)
					cv2.circle(zoom_grid, (threshX, threshY), 2, (255,255,255), 3)
					cv2.rectangle(zoom_grid, text_coords, (text_coords[0]+math.floor(1.4*zoom_grid_size), text_coords[1]+140), (55,55,55), -1)

					# re-fill in the text box because 128 overwrote the pixel values
					cv2.putText(zoom_grid, f"2dx: {pointB[0]*2}", (text_coords[0]+5, text_coords[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, f"2dy: {pointB[1]*2}", (text_coords[0]+5, text_coords[1]+45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, f"d_hat: {pixels[curr_x-1]['d_hat']}", (text_coords[0]+5, text_coords[1]+75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, "d_hat +=2dy" if pixels[curr_x-1]['d_hat'] <= 0 else "d_hat +=(2dy-2dx)", (text_coords[0]+5, text_coords[1]+105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, "Increment y? NO" if pixels[curr_x-1]['d_hat'] <= 0 else "Increment y? YES", (text_coords[0]+5, text_coords[1]+135), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
				
				# re-fill the main grid's prediction line, and current progress line
				coordA = convertCoords(pointA[0], pointA[1], window_width, window_height, grid_size)
				coordB = convertCoords(curr_x, slope*(curr_x), window_width, window_height, grid_size)
				cv2.line(grid, coordA, convertCoords(pointB[0], pointB[1], window_width, window_height, grid_size), (50,50,50), 4)
				cv2.line(grid, coordA, coordB, (255,255,255), 4)
				
				# show on both screens the updated values
				cv2.imshow(zoom_window_name, zoom_grid)
				cv2.imshow(window_name, grid)

			# if the slope of the line is > 1
			else:
				# traverse by the y coordinate
				curr_y = ePress//2

				# if this is a new Y to look at, show pre-filled pixel and values
				if ePress % 2 == 0:
					# reset the zoomed in grid back to beginning
					zoom_grid = orig_zoom_grid.copy()
					cv2.circle(zoom_grid, (threshX, threshY), 2, (255,255,255), 3)

					# calculate the offset to use for the zoomed in view of the grid
					curr_x = (curr_y-1)/slope % 1
					if curr_x > 0.5:
						curr_x -= 1

					# draw the line for the zoomed in grid and place the updated text in the window
					zoom_start_line = convertCoords(-1/slope+curr_x, -1, zoom_window_width, zoom_window_height, zoom_grid_size)
					zoom_end_line = convertCoords(2/slope+curr_x, 2, zoom_window_width, zoom_window_height, zoom_grid_size)
					text_coords = convertCoords(0.6, 0.4, zoom_window_width, zoom_window_height, zoom_grid_size)
						
					cv2.line(zoom_grid,zoom_start_line, zoom_end_line, (255,255,255), 1)
					cv2.rectangle(zoom_grid, text_coords, (text_coords[0]+math.floor(1.4*zoom_grid_size), text_coords[1]+140), (55,55,55), -1)

					cv2.putText(zoom_grid, f"2dx: {pointB[0]*2}", (text_coords[0]+5, text_coords[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, f"2dy: {pointB[1]*2}", (text_coords[0]+5, text_coords[1]+45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, f"d_hat: {pixels[curr_y-1]['d_hat']}", (text_coords[0]+5, text_coords[1]+75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, "d_hat +=2dx" if pixels[curr_y-1]['d_hat'] <= 0 else "d_hat +=(2dx-2dy)", (text_coords[0]+5, text_coords[1]+105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, "Increment x? NO" if pixels[curr_y-1]['d_hat'] <= 0 else "Increment x? YES", (text_coords[0]+5, text_coords[1]+135), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

				# once the user has seen the prediction, fill in the pixel and re-fill any which was overwritten
				else:
					fillXY(grid, pixels[curr_y]["x"], pixels[curr_y]["y"], window_width, window_height, grid_size)
					fillXY(zoom_grid, 0 if(pixels[curr_y]["x"] == pixels[curr_y-1]["x"]) else 1, 1, zoom_window_width, zoom_window_height, zoom_grid_size)

					cv2.line(zoom_grid,zoom_start_line, zoom_end_line, (255,255,255), 1)
					cv2.circle(zoom_grid, (threshX, threshY), 2, (255,255,255), 3)
					cv2.rectangle(zoom_grid, text_coords, (text_coords[0]+math.floor(1.4*zoom_grid_size), text_coords[1]+140), (55,55,55), -1)

					cv2.putText(zoom_grid, f"2dx: {pointB[0]*2}", (text_coords[0]+5, text_coords[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, f"2dy: {pointB[1]*2}", (text_coords[0]+5, text_coords[1]+45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, f"d_hat: {pixels[curr_y-1]['d_hat']}", (text_coords[0]+5, text_coords[1]+75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, "d_hat +=2dx" if pixels[curr_y-1]['d_hat'] <= 0 else "d_hat +=(2dx-2dy)", (text_coords[0]+5, text_coords[1]+105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
					cv2.putText(zoom_grid, "Increment x? NO" if pixels[curr_y-1]['d_hat'] <= 0 else "Increment x? YES", (text_coords[0]+5, text_coords[1]+135), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
								
				# re-fill master lines and display updated windows
				coordA = convertCoords(pointA[0], pointA[1], window_width, window_height, grid_size)
				coordB = convertCoords(curr_y/slope, curr_y, window_width, window_height, grid_size)
				cv2.line(grid, coordA, convertCoords(pointB[0], pointB[1], window_width, window_height, grid_size), (50,50,50), 4)
				cv2.line(grid, coordA, coordB, (255,255,255), 4)
				
				cv2.imshow(zoom_window_name, zoom_grid)
				cv2.imshow(window_name, grid)

			# if we have completed the line from pointA to pointB, fill all pixels with gold
			if ePress//2 == max(pointB[0], pointB[1]):
				grid[np.where((grid==[0,0,75]).all(axis=2))] = [0,205,255]
			
				cv2.imshow(window_name, grid)
				
				# reset variables
				slope = pointB[1]/pointB[0]
				ePress = 1
				grid = orig_grid.copy()
				pixels = bresenham(pointA[0], pointA[1], pointB[0], pointB[1])

				# reset circles
				grid = initPoints(grid, pointA, pointB, window_width, window_height, grid_size)
			
		key = cv2.waitKey()

	# quit
	if key == ord("q") or curr_x == pointB[0]:
		cv2.destroyAllWindows()
		quit()
	
	cv2.waitKey()


def convertCoords(pointX: float, pointY: float, window_width: int, window_height: int, grid_size: int):
	# Converts (X,Y) coordinates (pointX, pointY) to pixel values for screen use and returns them
	convX = math.floor(grid_size*pointX+grid_size)
	convY = math.floor(window_height - grid_size*pointY-grid_size)

	return convX, convY

def fillXY(grid: list, pointX: int, pointY: int, window_width: int, window_height: int, grid_size: int):
	# Fills the (pointX, pointY) coordinate with (0,0,75) maroon color representing the pixel being filled
	grid_coords = convertCoords(pointX, pointY, window_width, window_height, grid_size)
	
	topLeft = (grid_coords[0]-(grid_size//2)+1, grid_coords[1]-(grid_size//2)+1)
	bottomRight = (grid_coords[0]+(grid_size//2)-1, grid_coords[1]+(grid_size//2)-1)
	cv2.rectangle(grid, topLeft, bottomRight, (0,0,75),-1)
	
def initWindow(window_name: list, window_width: int, window_height: int, grid_size: int):
	# Initializes the OpenCV window with an empty grid
	cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
	cv2.resizeWindow(window_name, window_width,window_height)

	grid = initGrid(window_width, window_height, grid_size)
	return grid

def initPoints(grid: list, pointA: list, pointB: list, window_width: int, window_height: int, grid_size: int):
	# Initializes the points with a trace line connecting them
	fillXY(grid, pointA[0], pointA[1], window_width, window_height, grid_size)
	fillXY(grid, pointB[0], pointB[1], window_width, window_height, grid_size)
	
	pointA = convertCoords(pointA[0], pointA[1], window_width, window_height, grid_size)
	pointB = convertCoords(pointB[0], pointB[1], window_width, window_height, grid_size)
	cv2.circle(grid, pointA, 10, (255,255,255), -1)
	cv2.circle(grid, pointB, 10, (255,255,255), -1)
	
	cv2.line(grid, pointA, pointB, (50,50,50), 4)

	return grid

def bresenham(x1: int, y1: int, x2: int, y2: int):
	# performs the bresenham algorithm and returns the coordinates of pixels to be filled in between the two points
	out_arr = []
	dy = y2 - y1
	dx = x2 - x1

	two_dy = dy+dy
	two_dx = dx+dx

	if x2 > y2:
		y = y1
		d_hat = two_dy - dx
		for x in range(x1, x2+1):
			out_arr.append({"x": x,"y": y, "d_hat": d_hat})

			if(d_hat <= 0): # do not increment y for the next point, we are below the threshold still
				d_hat += two_dy
			else: # increment y, we are above the threshold
				y += 1
				d_hat = d_hat + two_dy - two_dx
	else:
		x = x1
		d_hat = two_dx - dy
		for y in range(y1, y2+1):
			out_arr.append({"x": x,"y": y, "d_hat": d_hat})

			if(d_hat <= 0): # do not increment y for the next point, we are below the threshold still
				d_hat += two_dx
			else: # increment y, we are above the threshold
				x += 1
				d_hat = d_hat + two_dx - two_dy


	return out_arr

def initGrid(window_width: int, window_height: int, grid_size: int):
	# create grid with black background and white dividers	
	grid = np.asarray([[[255,255,255] if ((x-grid_size//2)%grid_size==0 or (y+grid_size//2)%grid_size==0) else [0,0,0] for x in range(window_width)] for y in range(window_height)]).astype(np.uint8)

	# create plus signs in the center of each pixel, length of 6 and width of 1
	for x in range((grid_size//2)+round(0.5*grid_size), window_width, grid_size):
		for y in range((grid_size//2)-round(0.5*grid_size), window_height, grid_size):
			cv2.line(grid, (x-3,y), (x+3,y), (120,120,120), 1)
			cv2.line(grid, (x,y-3), (x,y+3), (120,120,120), 1)
	return grid
	
def launch_controls_window():
	# Creates the controls window to instruct the user on how to use the program
	cv2.namedWindow("controls")
	cv2.resizeWindow("controls", 200, 500)
	controls_background = np.zeros((200,500))
	cv2.putText(controls_background, "Controls:",(15,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255))
	cv2.putText(controls_background, "W: Move second point up",(15,55), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255))
	cv2.putText(controls_background, "A: Move second point left",(15,80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255))
	cv2.putText(controls_background, "S: Move second point down",(15,105), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255))
	cv2.putText(controls_background, "D: Move second point right",(15,130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255))
	cv2.putText(controls_background, "E: Advance Forward",(15,155), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255))
	cv2.putText(controls_background, "Q: Quit Program",(15,180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255))
	cv2.imshow("controls", controls_background)


if __name__ == "__main__":
	main()