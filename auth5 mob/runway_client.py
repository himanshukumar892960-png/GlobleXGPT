from runwayml import RunwayML
import os
import time

class RunwayClient:
    def __init__(self, api_key):
        self.client = RunwayML(api_key=api_key)

    def generate_video(self, prompt, image_url=None, model="gen3a_turbo"):
        """
        Generates a video from a text prompt or image + prompt.
        """
        try:
            print(f"Starting RunwayML video generation for: {prompt}")
            
            if image_url:
                # Image-to-Video
                try:
                    job = self.client.image_to_video.create(
                        model="gen3a_turbo",
                        prompt_image=image_url,
                        prompt_text=prompt,
                        duration=5,
                        ratio="1280:720"
                    )
                except Exception as e:
                    print(f"Gen-3 Turbo (Image) failed, trying veo3.1: {e}")
                    job = self.client.image_to_video.create(
                        model="veo3.1",
                        prompt_image=image_url,
                        prompt_text=prompt
                    )
            else:
                # Text-to-Video
                try:
                    # Try veo3.1 first as it might be the standard available model
                    job = self.client.text_to_video.create(
                        model="veo3.1",
                        prompt_text=prompt,
                        ratio="1280:720"
                    )
                except Exception as e:
                    print(f"veo3.1 (Text) failed, trying gen3a_turbo: {e}")
                    job = self.client.text_to_video.create(
                        model="gen3a_turbo",
                        prompt_text=prompt,
                        duration=5,
                        ratio="1280:720"
                    )
            
            task_id = job.id
            print(f"Task created with ID: {task_id}")

            # Poll for completion
            while True:
                task = self.client.tasks.retrieve(task_id)
                status = task.status
                print(f"Task {task_id} status: {status}")

                if status == "SUCCEEDED":
                    video_url = task.output[0]
                    return video_url
                elif status == "FAILED":
                    print(f"Task {task_id} failed: {task.error}")
                    return None
                
                # Wait before polling again
                time.sleep(10)
                
        except Exception as e:
            print(f"Error in RunwayML generation: {e}")
            return None

    def get_task_status(self, task_id):
        try:
            task = self.client.tasks.retrieve(task_id)
            return task
        except Exception as e:
            print(f"Error retrieving task: {e}")
            return None
