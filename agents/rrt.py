import arty


class RRT(arty.Arty):
    def future_position(self, pedestrian, time):
        return pedestrian.position  # don't extrapolate positions
