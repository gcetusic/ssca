# -*- coding: utf-8 -*-
from collections import defaultdict
try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None

def distance_squared(p1, p2):
    return (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2

def cluster_naive(points, size):
    """sequential search"""
    radius_sq = (size/2.)**2
    points = set(points)
    clusters = []
    while points:
        point = points.pop()
        cluster = [p2 for p2 in points if distance_squared(point, p2) <= radius_sq ]
        points.difference_update(cluster)
        cluster.append(point)
        clusters.append((point, cluster))
    return clusters


def cluster_smart(points, size):
    """prebinning"""
    # Precalculate some constants outside the loop
    inv_size = 1./size
    halfsize = size/2.
    radius_sq = halfsize**2
    
    points = set(points)
    
    # Register all points in bins
    bins = defaultdict(list)
    for p in points:
        bins[int(p[0]*inv_size), int(p[1]*inv_size)].append(p)
    
    clusters = []
    while points:
        point = iter(points).next() # pick arbitrary point, don't remove
        cluster = []
        
        coords = int(point[0]*inv_size), int(point[1]*inv_size)
        
        # which neighboring squares to investigate
        dx = -1 if (point[0] % size) < halfsize else 1
        dy = -1 if (point[1] % size) < halfsize else 1
        for bdx, bdy in [(0,0),(dx,0),(dx,dy),(0,dy)]:
            bincoords = coords[0]+bdx, coords[1]+bdy
            if bincoords not in bins:
                continue
            
            keep = [] # Collect points to keep
            for point2 in bins[bincoords]:
                if distance_squared(point, point2) <= radius_sq:
                    cluster.append(point2)
                else:
                    keep.append(point2)
            bins[bincoords] = keep
        points.difference_update(cluster) # Remove clustered points from consideration
        clusters.append((point, cluster))
        
    return clusters

class OrderingCluster(object):
    """Helper class that defines ordering methods to pick best cluster."""
    def __init__(self, point, items):
        self.point = point
        self.items = set(items)
    def __lt__(self, other):
        return len(self.items) > len(other.items)
    def __le__(self, other):
        return len(self.items) >= len(other.items)
    def __eq__(self, other):
        return len(self.items) == len(other.items)
    def __ge__(self, other):
        return len(self.items) < len(other.items)
    def __gt__(self, other):
        return len(self.items) < len(other.items)
    def update(self, removed):
        self.items = self.items - removed
    def __repr__(self):
        return "%s(%d)" % (self.point, len(self.items))

import heapq

def cluster_qt(points, size):
    """largest cluster first"""
    # Precalculate some constants outside the loop
    inv_size = 1./size
    halfsize = size/2.
    radius_sq = halfsize**2
    
    def near_point(point):
        """Helper function to find all points near a given point."""
        cluster = []
        coords = int(point[0]*inv_size), int(point[1]*inv_size)

        # which neighboring squares to investigate
        dx = -1 if (point[0] % size) < halfsize else 1
        dy = -1 if (point[1] % size) < halfsize else 1
        for bdx, bdy in [(0,0),(dx,0),(dx,dy),(0,dy)]:
            bin_coords = coords[0]+bdx, coords[1]+bdy
            if bin_coords not in bins:
                continue
            for point2 in bins[bin_coords]:
                if distance_squared(point, point2) <= radius_sq:
                    cluster.append(point2)
        return cluster

    points = set(points)
    
    # Prebin points
    bins = defaultdict(list)
    for p in points:
        bins[int(p[0]*inv_size), int(p[1]*inv_size)].append(p)
    
    clusters = []
    
    # Create a candidate cluster for each point and register in a priorityqueue
    candidate_clusters = []
    for point in points:
        candidate_clusters.append(OrderingCluster(point, near_point(point)))
    heapq.heapify(candidate_clusters)
    
    removed_points = set()
    while len(candidate_clusters) > 1:
        # Pick best cluster
        candidate = heapq.heappop(candidate_clusters)
        # Remove already clustered points
        candidate.update(removed_points)
        if not candidate.items: # Empty, discard
            continue
        while candidate > candidate_clusters[0]:
            # While current is no longer best pick and update next-one
            candidate = heapq.heapreplace(candidate_clusters, candidate)
            candidate.update(removed_points)
        if not candidate.items:
            continue
        # Select this cluster
        removed_points.update(candidate.items)
        clusters.append((candidate.point, list(candidate.items)))
    candidate = candidate_clusters.pop()
    if candidate.items:
        clusters.append((candidate.point, list(candidate.items)))

    return clusters

        
# Helpers for timing and visualization
from datetime import datetime

now = datetime.now
def duration(start, end):
    delta = end - start
    return (delta.seconds + delta.microseconds/1000000.)

def timed(func, *args, **kwargs):
    num_runs = kwargs.pop('num_runs', 1)
    times = []
    for run in xrange(num_runs):
        start = now()
        result = func(*args, **kwargs)
        end = now()
        times.append(duration(start, end))
    return result, min(times)


def draw_square(size, points, clusters, clustersize, draw_in_cluster=True):
    esize = clustersize*0.5
    img = Image.new('RGB', (size, size), '#FFFFFF')

    draw = ImageDraw.ImageDraw(img)
    drawn = set()
    for c, c_points in clusters:
        if len(c_points) > 1:
            draw.ellipse((c[0]-esize, c[1]-esize, c[0]+esize, c[1]+esize), fill='#CCCCFF' ,outline='#9999FF')
            drawn.update(c_points)
    for p in points:
        if draw_in_cluster or p not in drawn:
            draw.point(p, '#000000')
    return img

if __name__ == '__main__':
    from random import random, normalvariate, seed
    
    SIZE = 500
    CLUSTERS = 1000
    CLUSTER_POINTS = 10
    STDEV = 2
    
    def clamp(value):
        return max(0, min(SIZE, value))
    
    seed(0) # Seed random number generator for stable results
    cluster_centers = [(random()*SIZE, random()*SIZE) for i in xrange(CLUSTERS)]
    points = [(clamp(normalvariate(x, STDEV)), clamp(normalvariate(y, STDEV)))
         for x,y in cluster_centers for _ in xrange(CLUSTER_POINTS)]
    
    
    for cluster_diameter in [5, 10, 20, 40]:
        for cluster_func in [cluster_naive, cluster_smart, cluster_qt]:
            clusters, time_used = timed(cluster_func, points, cluster_diameter, num_runs=3)
            print("Cluster size %d with %s method, time %.2fms" % (cluster_diameter, cluster_func.__doc__, time_used*1000))
            n_markers = len(clusters)
            n_clusters = sum(1 for center, points in clusters if len(points) > 1)
            avg_size = sum(len(points) for center, points in clusters)/float(n_clusters)
            print("    markers=%d clusters=%d average size:%.2f" % (n_markers, n_clusters, avg_size))
            if Image:
                draw_square(SIZE, points, clusters, cluster_diameter).save('%s_%d.png' % (cluster_func.__name__, cluster_diameter))
