# --------------------------------------------
#   Name: Stuart Hamilton
#   ID: 1619864
#   CMPUT 274, Fall 2020
#
#   Assignment 2: Huffman Coding
# --------------------------------------------
import bitio
import huffman
import pickle


def read_tree(tree_stream):
    '''Read a description of a Huffman tree from the given compressed
    tree stream, and use the pickle module to construct the tree object.
    Then, return the root node of the tree itself.

    Args:
      tree_stream: The compressed stream to read the tree from.

    Returns:
      A Huffman tree root constructed according to the given description.
    '''
    tree = pickle.load(tree_stream)
    return tree


def decode_byte(tree, bitreader):
    """
    Reads bits from the bit reader and traverses the tree from
    the root to a leaf. Once a leaf is reached, bits are no longer read
    and the value of that leaf is returned.

    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.
      tree: A Huffman tree.

    Returns:
      Next byte of the compressed bit stream.
    """
    currNode = tree
    # Sets root node
    while True:
        try:
            if currNode.getValue() is not None:
                symbol = (currNode.getValue())
                break
                # If object is in class TreeLeaf returns ASCII integer byte
            else:
                raise EOFError
        except AttributeError:
            # If not in class Treeleaf the object is in class TreeBranch
            bit = bitreader.readbit()
            if bit == 0:
                currNode = currNode.getLeft()
            else:
                currNode = currNode.getRight()
            # Traverses tree to next branch where 0 is left and 1 is right
    return symbol


def decompress(compressed, uncompressed):
    '''First, read a Huffman tree from the 'compressed' stream using your
    read_tree function. Then use that tree to decode the rest of the
    stream and write the resulting symbols to the 'uncompressed'
    stream.

    Args:
      compressed: A file stream from which compressed input is read.
      uncompressed: A writable file stream to which the uncompressed
          output is written.
    '''
    output_stream = []
    tree = read_tree(compressed)
    read_bits = bitio.BitReader(compressed)
    try:
        while True:
            symbol = decode_byte(tree, read_bits)
            output_stream.append(symbol)
    except EOFError:
        compressed.close()
    compressed.close()
    # Each decoded ASCII integer (byte) is added to a list
    bit_writer = bitio.BitWriter(uncompressed)
    for single_byte in output_stream:
        bit_writer.writebits(single_byte, 8)
    bit_writer.flush()
    uncompressed.close()
    # Bitwriter writes out each byte as binary to the uncompressed stream
    pass


def write_tree(tree, tree_stream):
    '''Write the specified Huffman tree to the given tree_stream
    using pickle.

    Args:
      tree: A Huffman tree.
      tree_stream: The binary file to write the tree to.
    '''
    pickle.dump(tree, tree_stream)
    pass


def compress(tree, uncompressed, compressed):
    '''First write the given tree to the stream 'compressed' using the
    write_tree function. Then use the same tree to encode the data
    from the input stream 'uncompressed' and write it to 'compressed'.
    If there are any partially-written bytes remaining at the end,
    write 0 bits to form a complete byte.

    Flush the bitwriter after writing the entire compressed file.

    Args:
      tree: A Huffman tree.
      uncompressed: A file stream from which you can read the input.
      compressed: A file stream that will receive the tree description
          and the coded input data.
    '''
    write_tree(tree, compressed)
    mapping = huffman.make_encoding_table(tree)
    # Ditionary for mapping bytes to their bit encoding
    read_bits = bitio.BitReader(uncompressed)
    sequence_list = []
    try:
        while True:
            byte = read_bits.readbits(8)
            sequence_list.append(mapping[byte])
    except EOFError:
        uncompressed.close()
    # Appends each encoded bite sequencce for each byte written to a list
    try:
        sequence_list.append(mapping[None])
    except KeyError:
        uncompressed.close()
    uncompressed.close()
    # Adds EOF bit sequence if the key exists
    write_bits = bitio.BitWriter(compressed)
    for sequence in sequence_list:
        for bit in sequence:
            if bit is False:
                write_bits.writebit(False)
            else:
                write_bits.writebit(True)
    write_bits.flush()
    compressed.close()
    # Writes all the sequences in order bit by bit to the compressed stream
    pass
