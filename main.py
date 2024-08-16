from program import Program
import Utils
if __name__ == "__main__":
    program = Program(10, 10, "input.txt")
    with open("output.txt", "w") as file:
        file.write('troll\n')
    program.run()
    # rotationOrder = Utils.getRotationOrder(Utils.Direction.DOWN, Utils.Direction.RIGHT)
    # for order in rotationOrder:
    #     if order == Utils.Direction.LEFT:
    #         print('isL')
    #     elif order == Utils.Direction.RIGHT:
    #         print('isR')
