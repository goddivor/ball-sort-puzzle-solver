"""
Test script for multi-ball move logic
"""
from models.puzzle_solver import GameState

def test_multi_ball_moves():
    """Test that consecutive same-colored balls move together"""
    
    # Create test case: tube with 2 red balls on top, then blue
    red = (255, 0, 0)
    blue = (0, 0, 255)
    
    # Tube 1: [blue, red, red] (bottom to top)
    # Tube 2: empty
    tubes = [
        [blue, red, red],  # Tube 0
        []                 # Tube 1 (empty)
    ]
    
    state = GameState(tubes, 4)
    
    print("Initial state:")
    for i, tube in enumerate(state.tubes):
        print(f"Tube {i}: {tube}")
    
    # Test consecutive ball detection
    consecutive = state._get_consecutive_top_balls(0)
    print(f"\nConsecutive balls from tube 0 top: {consecutive}")
    print(f"Expected: 2 red balls, Got: {len(consecutive)} balls")
    
    # Test move validity (should be able to move 2 red balls to empty tube)
    is_valid = state._is_valid_move(0, 1)
    print(f"\nMove from tube 0 to tube 1 valid: {is_valid}")
    
    # Execute move
    if is_valid:
        new_state = state.make_move(0, 1)
        print("\nAfter move:")
        for i, tube in enumerate(new_state.tubes):
            print(f"Tube {i}: {tube}")
        
        print(f"\nExpected: Tube 0=[blue], Tube 1=[red, red]")

if __name__ == "__main__":
    test_multi_ball_moves()