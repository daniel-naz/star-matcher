from starmatcher import StarMatcher, Star, LineNode
import utils

matcher = StarMatcher(200)

stars1 = matcher.detect_stars("fr1.jpg")
stars2 = matcher.detect_stars("fr2.jpg")

graph1 = matcher.build_graph(stars1)
graph2 = matcher.build_graph(stars2)

StarMatcher.match_stars(graph1, graph2)