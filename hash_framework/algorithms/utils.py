import cmsh


def reshape(model: cmsh.Model, vec, num_elements: int, width: int):
    # Three types here that we support passing for vec
    #
    # - a cmsh.Vector instance -- we can reshape this to the correct size
    #   easily using split_vec.
    #
    # - int -- we can convert this to a vector of width num_elements * width
    #   and pass it to reshape (as it is now a Vector).
    #
    # - a list/tuple of (bools, ints, or Vectors) of potentially arbitrary
    #   widths. This is hardest to deal with. First, we expand ints to be of
    #   the passed width. Then we join the list/tuple into a single vector.
    #   This lets us validate the combined width of everything in the vector,
    #   before calling reshape on it.

    bitwidth = num_elements * width

    if isinstance(vec, cmsh.Vector):
        if len(vec) != bitwidth:
            msg = f"Expected vector to have {bitwidth} bits, but was instead "
            msg += f"of length {len(vec)}"
            raise ValueError(msg)

        ret = model.split_vec(vec, width)
        if num_elements == 1:
            return ret[0]

        return ret

    if isinstance(vec, int):
        new_vec = model.to_vector(vec, bitwidth)
        return reshape(model, new_vec, num_elements, width)

    if isinstance(vec, (list, tuple)):
        # Coerce to list and copy so we can modify the elements in it.
        vec = list(vec[:])
        for index, element in enumerate(vec):
            # Boolean is a subclass of int that we choose to ignore
            if isinstance(element, bool):
                continue

            if isinstance(element, int):
                vec[index] = model.to_vector(element, width)
            elif isinstance(element, (list, tuple, cmsh.Vector)):
                # For explicitly sized objects, don't attempt to resize them.
                vec[index] = model.to_vector(element)

        new_vec = model.join_vec(vec)
        return reshape(model, new_vec, num_elements, width)

    raise ValueError(f"Object was of unknown type: {type(vec)}")
