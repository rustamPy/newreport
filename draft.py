from typing import List
class Solution:
    def minOperations(self, boxes: str) -> List[int]:
        # [0, 0, 1, 0, 1, 1]
        N = len(boxes)
        all_balls = [0] * (N + 1)
        all_positions = [0] * (N + 1)

        for i in range(N):
            all_balls[i+1] = all_balls[i] + boxes[i]
        # [0 | 0, 0, 0, 0, 0, 0] -> [0 | 0, 0, 1, 1, 2, 3] 
        # for left_balls = all_balls[i]
        # for right_balls = all_balls[N] - left_balls

        for i in range(N):
            all_positions[i+1] = all_positions[i] + (i * boxes[i])
        #     [0, 1, 2, 3, 4, 5]
        #      *, *, *, *, *, *
        #     [0, 0, 1, 0, 1, 1]
        #     [+, +, +, +, +, +]
        #      
        # [0 | 0, 0, 0, 0, 0, 0]
        # [0 | 0, 0, 2, 2, 6, 11]
        # for left_distance = (left_balls * i) - all_positions[i]
        # for right_distance = (all_positions[n] - all_positions[i+1]) - (right_balls * i)

        for i in range(N):
            # [0, 0, 1, (0), 1, 1]

            # [0 | 0, 0, 2, 2, 6, 11]
            # i = 3
            # left_balls = 1
            # right_balls = all_balls - left_balls = 2
            



