import cv2
from starmatcher import StarMatcher, Star, LineNode
import utils

matcher = StarMatcher(60)

stars1 = matcher.detect_stars("ST_db1.png")
stars2 = matcher.detect_stars("ST_db2.png")

graph1 = matcher.build_graph(stars1)
graph2 = matcher.build_graph(stars2)

utils.draw_constellations("ST_db1.png", matcher, "graph1.jpg")
utils.draw_constellations("ST_db2.png", matcher, "graph2.jpg")

# utils.draw_stars("ST_db1.png", matcher, "graph1.jpg")
# utils.draw_stars("ST_db2.png", matcher, "graph2.jpg")

# utils.connect_images("graph1.jpg", "graph2.jpg", output_path="temp.jpg")

# matches = matcher.detect_matching_stars("ST_db1.png", "ST_db2.png", min_matches=15, match_offset=5)

# utils.draw_constellations("fr1.jpg", matcher, "graph1.jpg")
# utils.draw_constellations("zoomed.jpg", matcher, "graph2.jpg")

# utils.connect_images("graph1.jpg", "graph2.jpg", output_path="temp.jpg")

# matches = matcher.detect_matching_stars("fr1.jpg", "zoomed.jpg", min_matches=5)

# print("total matches found : ", len(matches))
# for i, j in matches:
#     print(f"{i} matches {j}")

