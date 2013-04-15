import math
import helpers

MAP_ZOOM = 21
MAP_OFFSET = 268435456    # half the Earth's circumference at zoom level 21
MAP_RADIUS = MAP_OFFSET / math.pi


def longitude_to_x(longitude):
    """
    Returns the x pixel coordinate for a given longitude value.
    Longitude values are in decimal degrees format.
    """
    x = round(MAP_OFFSET + MAP_RADIUS * longitude * math.pi / 180)

    return x


def latitude_to_y(latitude):
    """
    Returns the y pixel coordinate for a given latitude value.
    Latitude values are in decimal degrees format.
    """
    y = round(MAP_OFFSET - MAP_RADIUS *
              math.log((1 + math.sin(latitude * math.pi / 180)) /
                       (1 - math.sin(latitude * math.pi / 180))) / 2)

    return y


def plane_distance(latitude1, longitude1, latitude2, longitude2, zoom):
    """
    Given a pair of lat/long coordinates and a map zoom level, returns
    the distance between the two points in pixels
    """
    x1 = longitude_to_x(longitude1)
    y1 = latitude_to_y(latitude1)

    x2 = longitude_to_x(longitude2)
    y2 = latitude_to_y(latitude2)

    distance = int(math.sqrt((x1 - x2) ** 2) + math.sqrt((y1 - y2) ** 2))

    return distance >> (MAP_ZOOM - zoom)


def cluster(points, cluster_distance, zoom, *args):
    """
    Groups points that are less than cluster_distance pixels apart at
    a given zoom level into a cluster.
    """
    clusters = []

    while len(points) > 0:
        point1 = points.pop()

        cluster = []

        for point2 in points[:]:

            pixel_distance = plane_distance(point1[args[0]],
                                            point1[args[1]],
                                            point2[args[0]],
                                            point2[args[1]],
                                            zoom)
            if pixel_distance < cluster_distance:
                points.remove(point2)
                cluster.append(point2)

        # add the first point to the cluster
        if len(cluster) > 0:
            cluster.append(point1)
            clusters.append(cluster)
        else:
            clusters.append([point1])

    return [(centroid(cluster, args[0], args[1]), cluster) for cluster in clusters]

def smart_cluster(locations, cluster_distance, zoom, algorithm, *args):
    """
    Returns clusters for a list of locations
    
    Uses algorithms from https://gist.github.com/anonymous/204365/
    """        
    if algorithm == 'old': # fallback to old clustering algorithm
        return cluster(locations, cluster_distance, zoom, *args)    
    size = cluster_distance
    for div in xrange(1,zoom):
        size = int(math.ceil(size / (1.35*div)))    
    #print 'Cluster size: ', size
    points = loc2points(locations, *args)
    cluster_function = getattr(helpers, 'cluster_%s' % algorithm) or helpers.cluster_naive
    clusters = cluster_function(points, size) if points else []
    return format_clusters(clusters, locations, *args)

def loc2points(locations, *args):
    return [(loc[args[0]], loc[args[1]]) for loc in locations]

def point2loc(point, locations, *args):
    for loc in locations:
        if loc[args[0]] == point[0] and loc[args[1]] == point[1]:
            return loc
    return None

def format_clusters(clusters, locations, *args):
    formatted_clusters = []
    for c, c_points in clusters:
        formatted_clusters.append((c, [point2loc(point, locations, *args) for  point in c_points]))        
    return formatted_clusters

def centroid(cluster, *args):
    if type(cluster[0]) == dict:
        points = loc2points(cluster, *args)
    else:
        points = cluster    
    x, y = zip(*points)
    latitude = sum(x) / len(x)
    longitude = sum(y) / len(y)
    return (latitude, longitude)
