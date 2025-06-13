from torch.utils.data import Dataset


class TaskDataset(Dataset):
    """
    Wraps teacher-generated task assignments as training examples for student.
    Each example is a (prompt, target_json) pair.
    """
    def __init__(self, examples):
        self.examples = examples

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        return self.examples[idx]