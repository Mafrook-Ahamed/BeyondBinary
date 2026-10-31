"""Minimal Tkinter desktop interface for the BeyondBinary pipeline."""
from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from beyondbinary.ml.pipeline import run_pipeline


class BeyondBinaryApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("BeyondBinary — Local SOC Triage")
        root.geometry("720x460")
        root.minsize(620, 400)

        self.csv_path = tk.StringVar()
        self.model_path = tk.StringVar(value="artifacts/ddos_model.joblib")
        self.status = tk.StringVar(value="Choose a flow CSV and a trained model to begin.")

        frame = ttk.Frame(root, padding=18)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="BeyondBinary", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Local flow scoring and incident review", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 18))

        self._file_row(frame, "Flow CSV", self.csv_path, self._choose_csv)
        self._file_row(frame, "Model file", self.model_path, self._choose_model)

        self.run_button = ttk.Button(frame, text="Run analysis", command=self._run)
        self.run_button.pack(anchor="w", pady=(12, 8))
        ttk.Label(frame, textvariable=self.status, wraplength=660).pack(anchor="w", pady=(0, 8))
        self.output = tk.Text(frame, height=10, wrap="word", state="disabled")
        self.output.pack(fill="both", expand=True)

    def _file_row(self, parent: ttk.Frame, label: str, variable: tk.StringVar, callback) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text=label, width=12).pack(side="left")
        ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(row, text="Browse…", command=callback).pack(side="left")

    def _choose_csv(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if path:
            self.csv_path.set(path)

    def _choose_model(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Model files", "*.joblib *.pkl"), ("All files", "*.*")])
        if path:
            self.model_path.set(path)

    def _run(self) -> None:
        csv_path, model_path = self.csv_path.get().strip(), self.model_path.get().strip()
        if not csv_path or not Path(csv_path).is_file():
            messagebox.showerror("Missing input", "Select an existing flow CSV file.")
            return
        if not model_path or not Path(model_path).is_file():
            messagebox.showerror("Missing model", "Select an existing trained model file (.joblib).")
            return
        output_path = str(Path(csv_path).with_name("incident_queue.csv"))
        self.run_button.configure(state="disabled")
        self.status.set("Analysis running… Large CSV files may take time.")
        threading.Thread(target=self._worker, args=(csv_path, model_path, output_path), daemon=True).start()

    def _worker(self, csv_path: str, model_path: str, output_path: str) -> None:
        try:
            queue = run_pipeline(csv_path, model_path)
            queue.to_csv(output_path, index=False)
            review_count = int(queue["human_review_required"].sum())
            incident_count = int(queue.loc[queue["incident_id"].ne(""), "incident_id"].nunique())
            summary = (f"Processed {len(queue):,} flows.\n"
                       f"{review_count:,} require human review.\n"
                       f"{incident_count:,} correlated incidents.\n\n"
                       f"Output saved to:\n{output_path}\n\n"
                       "Review flags are model-generated leads, not confirmed attacks.")
            self.root.after(0, self._finish, summary, None)
        except Exception as exc:
            self.root.after(0, self._finish, "", str(exc))

    def _finish(self, summary: str, error: str | None) -> None:
        self.run_button.configure(state="normal")
        if error:
            self.status.set("Analysis failed.")
            messagebox.showerror("Analysis failed", error)
            return
        self.status.set("Analysis complete.")
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", summary)
        self.output.configure(state="disabled")


def main() -> None:
    root = tk.Tk()
    BeyondBinaryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
