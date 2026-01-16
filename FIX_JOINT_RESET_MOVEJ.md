# Joint Reset Fix - Using MoveJ Instead of MoveL

## The Problem

Previously, the reset function was using **MoveL** (Cartesian/linear motion) to move to position [0, 0, 100], which is NOT the same as resetting the **joints** to 0 degrees.

The issue:
- **MoveL** moves the tool to a Cartesian position in space
- **MoveJ** moves the joints themselves to specific angles
- The button says "Reset Joints (0,0,0)" but was actually doing a Cartesian movement

## The Solution

Changed the reset functionality to use **MoveJ** with all joints at 0.0 degrees.

### What Changed

#### 1. `src/config.py` - Added new constant

```python
RESET_JOINTS_POSITION = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
```

This defines the target joint angles (all joints at 0 degrees) for true joint reset.

#### 2. `src/util.py` - Added `move_j()` method

```python
def move_j(self, joint_pos, vel, ovl):
    if not self.robot:
        return -1
    return self.robot.MoveJ(
        joint_pos=joint_pos,
        tool=TOOL_ID,
        user=USER_ID,
        vel=vel,
        ovl=ovl,
        blendT=-1.0
    )
```

This method wraps the SDK's MoveJ function for joint-based movement.

#### 3. `src/gui.py` - Updated reset functions

Changed both `reset_joints()` and `move_to_reset()` to use:

```python
# Instead of:
error = self.connection.move_l(RESET_POSITION, RESET_VELOCITY, RESET_OVERDRIVE)

# Now uses:
error = self.connection.move_j(RESET_JOINTS_POSITION, RESET_VELOCITY, RESET_OVERDRIVE)
```

### Key Differences

| Aspect | MoveL (Old) | MoveJ (New) |
|--------|-------------|-----------|
| Motion Type | Cartesian/Linear | Joint-based |
| Target | Tool position in space [x,y,z,rx,ry,rz] | Joint angles [j1,j2,j3,j4,j5,j6] |
| Path | Straight line in Cartesian space | Individual joint motion |
| Reset Behavior | Moves to coordinate position | Resets joints to 0 degrees |
| Button Label Match | Misleading | Accurate |

## Why This Matters

1. **Accuracy**: Joint reset now actually resets joints to 0 degrees
2. **Safety**: Each joint moves independently to 0, avoiding risky combined motions
3. **Clarity**: Button behavior matches the label "Reset Joints (0,0,0)"
4. **Consistency**: Follow true robotic programming conventions

## Speed Configuration

Both methods use the same speed parameters:
- `RESET_VELOCITY = 5` (mm/s for Cartesian, degrees/s for joints)
- `RESET_OVERDRIVE = 100` (100% of set velocity)

The 0.5-second delay after movement remains in place to allow the robot to settle before GUI updates.

## Testing

After this fix, clicking "Reset Joints (0,0,0)" will:
1. Move all 6 joints to 0 degrees slowly (5 degrees/second)
2. Wait 0.5 seconds for motion to complete
3. Update all sliders to 0.0
4. Display position as X: 0.00  Y: 0.00  Z: 100.00 (after forward kinematics from joint 0 state)
5. Show success message

## Files Modified

- `src/config.py` - Added `RESET_JOINTS_POSITION` constant
- `src/util.py` - Added `move_j()` method, removed unused imports
- `src/gui.py` - Updated `reset_joints()` and `move_to_reset()` to use MoveJ

