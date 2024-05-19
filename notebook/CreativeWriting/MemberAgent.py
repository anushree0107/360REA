from prompt_concise import Meeting_prompt, Complete_prompt, summarize_experience_prompt, \
    summarize_local_experience_prompt, summarize_global_experience_prompt
from utils import requestLLM, extract_content


class Member:
    def __init__(self, role, task, total_task, members_experience=None):
        self.role = role
        self.task = task
        self.total_task = total_task
        self.members_experience = members_experience
        self.response = None
        self.feedback = {}
        self.experience = None
        self.history = []
        if members_experience is not None:
            self.history.append(
                "This is the experience from previous tasks. You can refer to it for future tasks.\n" + members_experience)
        else:
            self.history.append(
                ""
            )
        self.learnings = []
        self.tokens = 0

    def meeting(self, res_others):
        completion = requestLLM("\n There are others' work\n" + res_others,
                              Meeting_prompt.format(total_task=self.total_task))
        response = completion.choices[0].message.content.replace("*", "")
        self.tokens += completion.usage.total_tokens
        # print(response)
        self.history.append(
            "User\n\n" + "\n There are others' work\n" + res_others + Meeting_prompt.format(total_task=self.total_task))
        self.history.append("Member\n\n" + response)
        headings = ["Self-Evaluation Score and Feedback", "Peer Score and Feedback"]
        feedback_dict = extract_content(response, headings)
        self.feedback = feedback_dict
        return feedback_dict

    def complete_task(self, project, res_pre, feedback="", pre_exp=""):
        Complete_prompt_ = Complete_prompt.format(
            role=self.role,
            total_task=self.total_task,
            subtask=self.task,
            main_goals=project.goals,
            guidance=project.guidance
        )
        completion = requestLLM(res_pre + feedback + pre_exp,
            Complete_prompt_)
        response = completion.choices[0].message.content
        self.tokens += completion.usage.total_tokens
        self.history.append(
            "User\n\n" + res_pre + feedback + pre_exp + Complete_prompt_)
        self.history.append("Member\n\n" + response)
        self.response = response
        return response

    def summarize_local_experience(self, feedback_peer, pre_exp):
        Summarize_local_experience_prompt_ = summarize_local_experience_prompt.format(
            role=self.role,
            pre_exp=pre_exp
        )
        completion = requestLLM("\n".join(self.history) + "\nThe above is our previous conversation.\n" + feedback_peer,
                              Summarize_local_experience_prompt_)
        response = completion.choices[0].message.content
        self.tokens += completion.usage.total_tokens
        return response

    def summarize_global_experience(self, project, global_exp):
        summarize_global_experience_prompt_ = summarize_global_experience_prompt.format(
            role=self.role,
            total_task=self.total_task,
            main_goals=project.goals,
            guidance=project.guidance,
            subtask=self.task,
            global_exp=global_exp
        )
        completion = requestLLM(summarize_global_experience_prompt_, "")
        response = completion.choices[0].message.content
        self.tokens += completion.usage.total_tokens
        self.history.append(response)
        return response

    def generate_summary(self, guidance):
        # generate a summary of work and learnings
        completion = requestLLM(
            "\n".join(
                self.history) + "\nThe above is our previous conversation.\n" + "\nThis is the guidance given to you by the leader\n" + guidance,
            summarize_experience_prompt)
        response = completion.choices[0].message.content
        self.tokens += completion.usage.total_tokens
        self.experience = response
        return response
