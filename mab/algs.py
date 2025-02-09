import numpy as np

"""
    This class contains some MAB's algorithms.

    @author Alison Carrera

"""


class UCB1(object):
    def __init__(self, n_arms):
        """
            UCB1 constructor.

            :param n_arms: Number of arms which this instance need to perform.
        """
        self.number_of_selections = np.zeros(n_arms).astype(np.float)
        self.rewards = np.zeros(n_arms).astype(np.float)

    def select(self):
        """
            This method selects the best arm chosen by UCB1.

            :return: Return selected arm number.
                    Arm number returned is (n_arm - 1).

                    Returns a list of arms by importance.
                    The chosen arm is the index 0 of this list.
        """

        arm_dont_usage = np.where(self.number_of_selections == 0)[0]
        if len(arm_dont_usage) > 0:
            self.number_of_selections[arm_dont_usage[0]] += 1

            ranked_arms = list(range(len(self.number_of_selections)))

            if arm_dont_usage[0] != 0:
                ranked_arms = np.roll(ranked_arms, 1)
                first_element = ranked_arms[0]
                index_current = ranked_arms.tolist().index(arm_dont_usage[0])

                ranked_arms[0] = arm_dont_usage[0]
                ranked_arms[index_current] = first_element

            return arm_dont_usage[0], ranked_arms

        average_reward = self.rewards / self.number_of_selections
        total_counts = np.sum(self.number_of_selections)

        ucb_values = self._factor_importance_each_arm(
            total_counts,
            self.number_of_selections,
            average_reward
        )
        ranked_arms = np.flip(np.argsort(ucb_values), axis=0)
        chosen_arm = ranked_arms[0]

        self.number_of_selections[chosen_arm] += 1

        return chosen_arm, ranked_arms

    def _factor_importance_each_arm(self, counts, num_selections, avg_reward):
        """
            This method represents the core of the UCB1 algorithm.

            :return: An array with the importance of all arms.
        """

        exploration_factor = np.sqrt(2 * np.log(counts) / num_selections)
        return avg_reward + exploration_factor

    def reward(self, chosen_arm, assign_reward = 1):
        """
            This method gives a reward for a given arm.

            :param chosen_arm: Value returned from select().
	    :param assign_reward: The reward given to the arm (default to 1).
        """
        self.rewards[chosen_arm] += assign_reward


class UCBTuned(UCB1):
    def __init__(self, n_arms):
        """
            UCB1 constructor.

            :param n_arms: Number of arms which this instance need to perform.
        """
        super().__init__(n_arms)

    def _factor_importance_each_arm(self, counts, num_selections, avg_reward):
        """
            This method represents the core of the UCB-Tuned algorithm.

            :return: An array with the importance of all arms.
        """
        variance_factor = avg_reward - np.square(avg_reward)

        tuned = np.sqrt(2 * np.log(counts) / num_selections)
        tuned_factor = variance_factor + tuned

        explo = np.minimum(1/4, tuned_factor)
        exploration_factor = np.sqrt((np.log(counts) / num_selections) * explo)

        return avg_reward + exploration_factor


class ThompsomSampling:
    def __init__(self, n_arms):
        """
            Thompsom Sampling constructor.

            :param n_arms: Number of arms which this instance need to perform.
        """
        self.number_reward_0 = np.zeros(n_arms).astype(np.float)
        self.number_reward_1 = np.zeros(n_arms).astype(np.float)

    def select(self):
        """
            This method selects the best arm chosen by Thompsom Sampling.

            :return: Return selected arm number.
                    Arm number returned is (n_arm - 1).

                    Returns a list of arms by importance.
                    The chosen arm is the index 0 of this list.
        """
        theta_value = np.random.beta(
            self.number_reward_1 + 1, self.number_reward_0 + 1
        )

        ranked_arms = np.flip(np.argsort(theta_value), axis=0)
        chosen_arm = ranked_arms[0]

        return chosen_arm, ranked_arms


    def reward(self, chosen_arm, assign_reward = 1):
        """
            This method gives a reward for a given arm.

            :param chosen_arm: Value returned from select().
	    :param assign_reward: The reward given to the arm (default to 1).
        """
        self.number_reward_1[chosen_arm] += assign_reward



    def penalty(self, chosen_arm):
        """
            This method gives a penalty for a given arm.
            It should be used in a onDestroy() event from a banner,
            for example.
            The arm was selected, showed to the user, but no interation
            was realized until the end of the arm cycle.

            :param chosen_arm: Value returned from select().
        """
        self.number_reward_0[chosen_arm] += 1
