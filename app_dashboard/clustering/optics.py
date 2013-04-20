import math

###############################################################################
# POINT
###############################################################################


class Point:

    def __init__(self, latitude, longitude):

        self.latitude = latitude
        self.longitude = longitude
        self.cd = None              # core distance
        self.rd = None              # reachability distance
        self.processed = False      # has this point been processed?

    # -------------------------------------------------------------------------
    # calculate the distance between any two points on earth
    # -------------------------------------------------------------------------

    def distance(self, point):

        # convert coordinates to radians

        p1_lat, p1_lon, p2_lat, p2_lon = [math.radians(c) for c in
            self.latitude, self.longitude, point.latitude, point.longitude]

        numerator = math.sqrt(
            math.pow(math.cos(p2_lat) * math.sin(p2_lon - p1_lon), 2) +
            math.pow(
                math.cos(p1_lat) * math.sin(p2_lat) -
                math.sin(p1_lat) * math.cos(p2_lat) *
                math.cos(p2_lon - p1_lon), 2))

        denominator = (
            math.sin(p1_lat) * math.sin(p2_lat) +
            math.cos(p1_lat) * math.cos(p2_lat) *
            math.cos(p2_lon - p1_lon))

        # convert distance from radians to meters
        # note: earth's radius ~ 6372800 meters

        return math.atan2(numerator, denominator) * 6372800

    # -------------------------------------------------------------------------
    # point as GeoJSON
    # -------------------------------------------------------------------------

    def to_geo_json_dict(self, properties=None):

        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [
                    self.longitude,
                    self.latitude,
                ]
            },
            'properties': properties,
        }

###############################################################################
# CLUSTER
###############################################################################


class Cluster:

    def __init__(self, points):

        self.points = points

    # -------------------------------------------------------------------------
    # calculate the centroid for the cluster
    # -------------------------------------------------------------------------

    def centroid(self):

        return Point(sum([p.latitude for p in self.points]) / len(self.points),
            sum([p.longitude for p in self.points]) / len(self.points))

    # -------------------------------------------------------------------------
    # calculate the region (centroid, bounding radius) for the cluster
    # -------------------------------------------------------------------------

    def region(self):

        centroid = self.centroid()
        radius = reduce(lambda r, p: max(r, p.distance(centroid)), self.points)
        return centroid, radius

    # -------------------------------------------------------------------------
    # cluster as GeoJSON
    # -------------------------------------------------------------------------

    def to_geo_json_dict(self, user_properties=None):

        center, radius = self.region()
        properties = {'radius': radius}
        if user_properties:
            properties.update(user_properties)

        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [
                    center.longitude,
                    center.latitude,
                ]
            },
            'properties': properties,
        }

###############################################################################
# OPTICS
###############################################################################


class Optics:

    def __init__(self, points, max_radius, min_cluster_size):

        self.points = points
        self.max_radius = max_radius               # maximum radius to consider
        self.min_cluster_size = min_cluster_size   # minimum points in cluster

    # -------------------------------------------------------------------------
    # get ready for a clustering run
    # -------------------------------------------------------------------------

    def _setup(self):

        for p in self.points:
            p.rd = None
            p.processed = False
        self.unprocessed = [p for p in self.points]
        self.ordered = []

    # -------------------------------------------------------------------------
    # distance from a point to its nth neighbor (n = min_cluser_size)
    # -------------------------------------------------------------------------

    def _core_distance(self, point, neighbors):

        if point.cd is not None:
            return point.cd
        if len(neighbors) >= self.min_cluster_size - 1:
            sorted_neighbors = sorted([n.distance(point) for n in neighbors])
            point.cd = sorted_neighbors[self.min_cluster_size - 2]
            return point.cd

    # -------------------------------------------------------------------------
    # neighbors for a point within max_radius
    # -------------------------------------------------------------------------

    def _neighbors(self, point):

        return [p for p in self.points if p is not point and
            p.distance(point) <= self.max_radius]

    # -------------------------------------------------------------------------
    # mark a point as processed
    # -------------------------------------------------------------------------

    def _processed(self, point):

        point.processed = True
        self.unprocessed.remove(point)
        self.ordered.append(point)

    # -------------------------------------------------------------------------
    # update seeds if a smaller reachability distance is found
    # -------------------------------------------------------------------------

    def _update(self, neighbors, point, seeds):

        # for each of point's unprocessed neighbors n...

        for n in [n for n in neighbors if not n.processed]:

            # find new reachability distance new_rd
            # if rd is null, keep new_rd and add n to the seed list
            # otherwise if new_rd < old rd, update rd

            new_rd = max(point.cd, point.distance(n))
            if n.rd is None:
                n.rd = new_rd
                seeds.append(n)
            elif new_rd < n.rd:
                n.rd = new_rd

    # -------------------------------------------------------------------------
    # run the OPTICS algorithm
    # -------------------------------------------------------------------------

    def run(self):

        self._setup()

        # for each unprocessed point (p)...

        while self.unprocessed:
            point = self.unprocessed[0]

            # mark p as processed
            # find p's neighbors

            self._processed(point)
            point_neighbors = self._neighbors(point)

            # if p has a core_distance, i.e has min_cluster_size - 1 neighbors

            if self._core_distance(point, point_neighbors) is not None:

                # update reachability_distance for each unprocessed neighbor

                seeds = []
                self._update(point_neighbors, point, seeds)

                # as long as we have unprocessed neighbors...

                while(seeds):

                    # find the neighbor n with smallest reachability distance

                    seeds.sort(key=lambda n: n.rd)
                    n = seeds.pop(0)

                    # mark n as processed
                    # find n's neighbors

                    self._processed(n)
                    n_neighbors = self._neighbors(n)

                    # if p has a core_distance...

                    if self._core_distance(n, n_neighbors) is not None:

                        #update reachability_distance for each of n's neighbors

                        self._update(n_neighbors, n, seeds)

        # when all points have been processed
        # return the ordered list

        return self.ordered

    # -------------------------------------------------------------------------

    def cluster(self, cluster_threshold):

        clusters = []
        separators = []

        i = 0
        while i < len(self.ordered) - 1:

            this_i = i
            next_i = i + 1
            this_p = self.ordered[i]
            next_p = self.ordered[next_i]
            this_rd = this_p.rd if this_p.rd else float('infinity')
            next_rd = next_p.rd if next_p.rd else float('infinity')

            # use an upper limit to separate the clusters

            if this_rd > cluster_threshold:
                separators.append(this_i)
            elif next_rd > cluster_threshold:
                separators.append(next_i)
                i += 1

            # use a jump metric to separate the clusters
            #
            # if this_rd - next_rd > cluster_threshold:
            #    separators.append(this_i)
            # elif next_rd - this_rd > cluster_threshold:
            #    separators.append(next_i)
            #    i += 1

            i += 1

        for i in range(len(separators) - 1):
            start = separators[i] + 1
            end = separators[i + 1]
            if end - start > self.min_cluster_size:
                clusters.append(Cluster(self.ordered[start:end]))

        return clusters


def blah(locations):
    points = []
    coordinates = locations.values_list('latitude', 'longitude')
    for i in coordinates:
        points.append(Point(float(i[0]), float(i[1])))

    return points

# LOAD SOME POINTS

# optics = Optics(points, 200, 5)   # 200 meter radius for neighbor consideration
# ordered = optics.run()
# clusters = optics.cluster(100)    # 100 meter threshold for clustering
