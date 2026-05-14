import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import sys

def visualize_log(log_filename):
    try:
        with open(log_filename, 'r') as f:
            log_text = f.read()
    except FileNotFoundError:
        print(f"Error: {log_filename} not found.")
        return

    pos_pattern = re.compile(r"The current position is ([\d\.-]+) ([\d\.-]+)")
    rem_pattern = re.compile(r"Removed edge from (\w+) to (\w+)")
    
    path = [tuple(map(float, m)) for m in pos_pattern.findall(log_text)]
    removals = rem_pattern.findall(log_text)
    
    obs_set = re.search(r"Obstacles: \{(.*?)\}", log_text)
    test_obs = [o.strip("' ") for o in obs_set.group(1).split(',')]
    

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 4.0); ax.set_ylim(0, 2.0); ax.set_aspect('equal')
    
    ax.add_patch(patches.Rectangle((0, 0), 0.8, 2.0, color='blue', alpha=0.05))
    ax.text(0.4, 1.9, 'Landing/Mission', ha='center', fontweight='bold', color='blue')
    
    ax.add_patch(patches.Rectangle((0.8, 0), 2.0, 2.0, color='orange', alpha=0.05))
    ax.text(1.8, 1.9, 'Obstacle Zone', ha='center', fontweight='bold', color='orange')
    
    ax.add_patch(patches.Rectangle((3.4, 0), 0.6, 2.0, color='green', alpha=0.05))
    ax.text(3.7, 1.9, 'Goal Zone', ha='center', fontweight='bold', color='green')

    nodes = {
        'A1': (1.1, 1.5), 'A2': (1.1, 1.0), 'A3': (1.1, 0.5),
        'B1': (1.8, 1.5), 'B2': (1.8, 1.0), 'B3': (1.8, 0.5),
        'C1': (2.6, 1.5), 'C2': (2.6, 1.0), 'C3': (2.6, 0.5),
        'D': (3.0, 1.5), 'GOAL': (3.7, 1.5)
    }
    
    for name, pos in nodes.items():
        ax.scatter(pos[0], pos[1], c='gray', s=10, alpha=0.3)
        ax.text(pos[0], pos[1]-0.08, name, fontsize=8, ha='center', color='gray')
    
    for obs in test_obs:
        mid_x = nodes.get(obs)[0] - 0.4
        mid_y = nodes.get(obs)[1]
        
        rect = patches.Rectangle((mid_x-0.1, mid_y-0.25), 0.2, 0.5, facecolor='white',
                                 edgecolor='black', hatch='//', alpha=0.3, zorder=2)
        ax.add_patch(rect)
    

    if path:
        x, y = zip(*path)
        ax.plot(x, y, 'r-', linewidth=2, label='Actual Robot Path', zorder=3)
        
        ax.scatter(x[0], y[0], color='green', s=100, edgecolors='black', label='Start', zorder=5)
        ax.text(x[0], y[0]+0.1, 'START', color='green', fontweight='bold', ha='center')
        
        ax.scatter(x[-1], y[-1], color='red', marker='X', s=100, edgecolors='black', label='Finish', zorder=5)
        ax.text(x[-1], y[-1]+0.1, 'FINISH', color='red', fontweight='bold', ha='center')
    
    
    for u, v in removals:
        if u in nodes and v in nodes:
            u_p, v_p = nodes[u], nodes[v]
            ax.plot([u_p[0], v_p[0]], [u_p[1], v_p[1]], 'rx--', alpha=0.6)
            ax.text((u_p[0]+v_p[0])/2, (u_p[1]+v_p[1])/2 + 0.05, 'BLOCKED', color='red', fontsize=7, ha='center')

    plt.title(f"Navigation Trace: {log_filename}", pad=20)
    plt.xlabel("X (meters)"); plt.ylabel("Y (meters)")
    plt.grid(True, linestyle=':', alpha=0.3)
    plt.legend(loc='lower left', fontsize='small')
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        target_file = 'robot_output.txt'
        
    visualize_log(target_file)




