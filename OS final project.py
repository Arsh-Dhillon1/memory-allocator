import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import matplotlib.cm as cm  # Import colormap module

class MemoryBlock:
    """
    Represents a block of memory.
    """
    def __init__(self, start, size, status="free", process_id=None):
        self.start = start
        self.size = size
        self.status = status
        self.process_id = process_id

    def __repr__(self):
        return f"Block(start={self.start}, size={self.size}, status='{self.status}', pid={self.process_id})"


class MemoryTracker:
    """
    Manages and tracks memory allocation.
    """
    def __init__(self, memory_size):
        self.memory_size = memory_size
        self.memory = [MemoryBlock(0, memory_size)]
        self.process_count = 0  # Track the number of processes

    def allocate(self, size, allocation_strategy="first_fit"):
        """
        Allocates a block of memory for a process.
        """
        if allocation_strategy == "first_fit":
            return self._allocate_first_fit(size)
        elif allocation_strategy == "best_fit":
            return self._allocate_best_fit(size)
        elif allocation_strategy == "worst_fit":
            return self._allocate_worst_fit(size)
        else:
            print(f"Invalid allocation strategy: {allocation_strategy}. Using first-fit.")
            return self._allocate_first_fit(size)

    def _allocate_first_fit(self, size):
        """First Fit Allocation Strategy"""
        for i, block in enumerate(self.memory):
            if block.status == "free" and block.size >= size:
                return self._split_and_allocate(i, size)
        return None  # Not enough memory

    def _allocate_best_fit(self, size):
        """Best Fit Allocation Strategy"""
        best_fit_index = -1
        min_size = float('inf')
        for i, block in enumerate(self.memory):
            if block.status == "free" and block.size >= size:
                if block.size < min_size:
                    min_size = block.size
                    best_fit_index = i
        if best_fit_index != -1:
            return self._split_and_allocate(best_fit_index, size)
        return None

    def _allocate_worst_fit(self, size):
        """Worst Fit Allocation Strategy"""
        worst_fit_index = -1
        max_size = -1
        for i, block in enumerate(self.memory):
            if block.status == "free" and block.size >= size:
                if block.size > max_size:
                    max_size = block.size
                    worst_fit_index = i
        if worst_fit_index != -1:
            return self._split_and_allocate(worst_fit_index, size)
        return None

    def _split_and_allocate(self, index, size):
        """Helper function to split a memory block and allocate part of it."""
        block = self.memory[index]
        self.process_count += 1  # Increment process counter for unique ID
        if block.size == size:
            block.status = "allocated"
            block.process_id = self.process_count
            return block.start
        else:
            allocated_block = MemoryBlock(block.start, size, "allocated", self.process_count)
            free_block = MemoryBlock(block.start + size, block.size - size)
            self.memory[index:index + 1] = [allocated_block, free_block]
            return allocated_block.start

    def deallocate(self, start):
        """
        Deallocates the memory block starting at the given address.
        """
        for block in self.memory:
            if block.start == start and block.status == "allocated":
                block.status = "free"
                block.process_id = None  # Clear the process ID
                self.merge_free_blocks()  # Merge after setting to free.
                return True
        return False  # Block not found or not allocated

    def merge_free_blocks(self):
        """
        Merges adjacent free memory blocks into a single larger block.
        """
        i = 0
        while i < len(self.memory) - 1:
            if self.memory[i].status == "free" and self.memory[i + 1].status == "free":
                self.memory[i].size += self.memory[i + 1].size
                del self.memory[i + 1]
            else:
                i += 1

    def get_memory_status(self):
        """
        Returns the current status of the memory.
        """
        return self.memory

    def get_free_memory(self):
        """
        Calculates the total amount of free memory.
        """
        return sum(block.size for block in self.memory if block.status == "free")

    def get_allocated_memory(self):
        """
        Calculates the total amount of allocated memory.
        """
        return sum(block.size for block in self.memory if block.status == "allocated")

    def get_fragmentation(self):
        """
        Calculates the external fragmentation as a percentage of total memory.
        """
        if not self.memory:
            return 0.0
        free_size = sum(block.size for block in self.memory if block.status == "free")
        return (free_size / self.memory_size) * 100 if self.memory_size else 0.0

    def get_free_blocks_count(self):
        """Returns the number of free blocks"""
        return sum(1 for block in self.memory if block.status == 'free')

# --- Visualization ---

def visualize_memory(memory_status, ax, memory_size, tracker):
    """
    Visualizes the memory allocation using matplotlib.
    """
    ax.clear()
    y = 0
    height = 1
    ax.set_xlim(0, memory_size)
    ax.set_ylim(0, height + 1)
    ax.set_title("Memory Allocation Status")
    ax.set_xlabel("Memory Address")
    ax.set_ylabel("Memory Blocks")

    for block in memory_status:
        if block.status == "free":
            color = "lightgreen"
        elif block.status == "allocated":
            if block.process_id is not None:
                color_map = cm.get_cmap('viridis')
                color = color_map(block.process_id / tracker.process_count) if tracker.process_count > 0 else 'red'
            else:
                color = 'red'  # error case.

        rect = plt.Rectangle((block.start, y), block.size, height, color=color)
        ax.add_patch(rect)

        # Process ID display
        if block.status == "allocated" and block.process_id is not None:
            text_x = block.start + block.size / 2
            ax.text(text_x, y + height / 2, f"PID:{block.process_id}",
                    ha='center', va='center', color='white', fontsize=8)

        # Free block label and address range
        elif block.status == 'free':
            text_x = block.start + block.size / 2
            ax.text(text_x, y + height / 2, f"Free\n[{block.start}-{block.start + block.size}]",
                    ha='center', va='center', color='black', fontsize=8)

    free_mem = tracker.get_free_memory()
    alloc_mem = tracker.get_allocated_memory()
    frag = tracker.get_fragmentation()
    free_blocks = tracker.get_free_blocks_count()

    info_text = f"Total Memory: {memory_size}\nFree Memory: {free_mem}\nAllocated Memory: {alloc_mem}\nFragmentation: {frag:.2f}%\nFree Blocks: {free_blocks}"
    ax.text(0.01, 0.95, info_text, transform=ax.transAxes, verticalalignment='top', fontsize=10)

def update(frame, tracker, fig, ax, memory_size):
    """
    Update function for the animation. This function is called repeatedly.
    """
    # Simulate allocation and deallocation
    if random.random() < 0.3:  # 30% chance of allocation
        size = random.randint(1, memory_size // 5)
        strategy = random.choice(["first_fit", "best_fit", "worst_fit"])
        start = tracker.allocate(size, strategy)
        if start is not None:
            print(f"Allocated {size} at {start} using {strategy}")
        else:
            print(f"Failed to allocate {size} using {strategy}")
    if random.random() < 0.1:  # 10% chance of deallocation
        if any(block.status == 'allocated' for block in tracker.get_memory_status()):
            allocated_blocks = [b for b in tracker.get_memory_status() if b.status == 'allocated']
            block_to_deallocate = random.choice(allocated_blocks)
            tracker.deallocate(block_to_deallocate.start)
            print(f"Deallocated memory at {block_to_deallocate.start}")

    # Update the visualization
    memory_status = tracker.get_memory_status()
    visualize_memory(memory_status, ax, memory_size, tracker)
    return ax,  # Return the artists that were updated

if __name__ == "__main__":
    memory_size = 100  # Total memory size
    tracker = MemoryTracker(memory_size)

    fig, ax = plt.subplots()
    visualize_memory(tracker.get_memory_status(), ax, memory_size, tracker)

    ani = animation.FuncAnimation(fig, update, fargs=(tracker, fig, ax, memory_size), interval=500, blit=False)

    plt.show()