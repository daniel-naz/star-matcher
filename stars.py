from starmatcher import StarMatcher, Star, LineNode
import utils

matcher = StarMatcher(200)

stars1 = matcher.detect_stars("fr1.jpg")
stars2 = matcher.detect_stars("fr2_180.jpg")

graph1 = matcher.build_graph(stars1)
graph2 = matcher.build_graph(stars2)

utils.draw_graph("fr1.jpg", matcher, "graph1.jpg")
utils.draw_graph("fr2_180.jpg", matcher, "graph2.jpg")
utils.connect_images("graph1.jpg", "graph2.jpg")

StarMatcher.match_stars(graph1, graph2)