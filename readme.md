# Summary 
In this assignment, we will develop an algorithm for star classification (identification). Given an image of stars.

## Part 1 - The Algorithm

The algorithm is based on the following presentation : [Link](https://sites.astro.caltech.edu/~moncelsi/FTS_talk.pdf).

The algorithm follows these steps:
1. 'Split' the images into a grid.
2. Take the 'n' brightest stars in each cell of the grid.
3. Pick 4 random stars and construct a geometric feature with 4 sides (quadrilateral).

   The 2 most distant stars are labelled A, B and are used to establish a local coordinate frame.

   The other stars are labelled C, D and they are used to compare 2 shapes.
4. Build 'n' geometric features in each cell.
5. Compare the features from the 2 images.

## Part 2 - Star Identification

We use the [```feature.blob_log```](https://scikit-image.org/docs/stable/api/skimage.feature.html#skimage.feature.blob_log) 
to locate the stars.

Our function recieves 4 variables ```image, min_sigma, max_sigma, threshold```.

- image - Path to image file / image file.
- min_sigma - Approx min size of a star.
- max_sigma - Approx max size of a star.
- threshold - Min brightness to classify as star, set heigher (aroud 0.1) for images with a lot of light pollution, smaller values (0.02) work well from clear dark skies. 

![locating-stars-1](/readmefiles/locating-stars-1.jpg)
![locating-stars-2](/readmefiles/locating-stars-2.jpg)


## Part 3 - Star Matching 

Here we use the algorithm talked about it Part 1, we first split the image into cells and build geometric features.

