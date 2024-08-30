import cv2
import numpy as np
import subprocess
import os

def motion_detection(video_path, output_dir):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("\033[91mError opening video\033[0m")

    prev_frame = None
    motion_start = None
    motion_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.uint8)
        blur_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

        if prev_frame is not None:
            diff = cv2.absdiff(blur_frame, prev_frame)
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 100]

            if len(contours) > 0:
                # Motion detected
                if motion_start is None:
                    motion_start = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

            elif motion_start is not None:
                # Motion ended
                motion_end = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

                motion_duration = motion_end - motion_start
                motion_path = f"{output_dir}/clip_{motion_count}.mp4"

                if motion_duration >= 0.5:
                    # Extract clip
                    subprocess.call([
                        "ffmpeg",
                        "-i", video_path,
                        "-ss", f"{motion_start-1:.2f}",
                        "-to", f"{motion_end+1:.2f}",
                        "-c:v", "copy",
                        "-c:a", "copy",
                        motion_path
                    ])
                    motion_count += 1
                motion_start = None

        prev_frame = blur_frame

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    input_dir = os.path.dirname(os.path.realpath(__file__))

    for filename in os.listdir(input_dir):
        if filename.endswith(".dav"):
            output_dir = r".\Clips" + "\\" + filename[13:-4]

            # Create a directory for each .dav file
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"Directory created: {output_dir}")

            video_path = os.path.join(input_dir, filename)
            print(f"Processing video: {filename}")
            motion_detection(video_path, output_dir)
