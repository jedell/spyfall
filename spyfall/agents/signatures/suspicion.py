import dspy

class Suspicion(dspy.Signature):
    """
    The dialogue history is from the game Spyfall, where players are given a location and a role with one player secretly being the spy.
    The spy does not know the location or role of the other players, nor are the other players aware the roles of anyone other than themselves. 
    The non-spy players must deduce who the spy is based on a series of questions and answers among the players, while the spy must attempt to deduce the location.
    The game ends if the spy successfully deduces the location or if the non-spy players successfully guess who the spy is.
    Using the dialogue history, output a float between 0 and 1, inclusive, representing how likely each agent is to be the spy.
    """

    dialogue_history = dspy.InputField(
        desc="The dialogue history from the game Spyfall.",
    )
    suspicion = dspy.OutputField(
        desc="The suspicion that each agent is the spy. Output format: <agent_name>: <suspicion>\\n<agent_name>: <suspicion>\\n<agent_name>: <suspicion>",
    )


if __name__ == "__main__":
    suspicion = dspy.Predict(Suspicion)

    print(suspicion(
        dialogue_history="""
[Step 1]: '<Player agent_3> asked <Player agent_2>: What's your favorite tool to use in your line of work?.'
[Step 2]: '<Player agent_2> answered <Player agent_3>: My favorite tool to use in my line of work is definitely my clipboard. It helps me keep track of inventory, schedules, and any important information I need to have on hand. What about you, what's your go-to tool for your job?.'
[Step 8]: '<Player agent_1> asked <Player agent_3>: What kind of clothing are people wearing at this location?.'
[Step 9]: '<Player agent_3> answered <Player agent_1>: At this location, people are usually wearing practical and comfortable clothing suited for working with tools and machinery. It's important to be able to move freely and stay clean while getting the job done..'
[Step 15]: '<Player agent_0> asked <Player agent_3>: What is your favorite part about working at this location?.'
[Step 16]: '<Player agent_3> answered <Player agent_0>: My favorite part about working at this location is being able to help people out when they have car troubles. It's satisfying to use my skills to fix their vehicles and get them back on the road quickly..'
[Step 22]: '<Player agent_1> asked <Player agent_3>: What specific tools or equipment do you use most often at this location?.'
[Step 23]: '<Player agent_3> answered <Player agent_1>: At this location, I find myself using wrenches and screwdrivers quite frequently. They are essential for the majority of repairs we handle here..'
[Step 29]: '<Player agent_2> asked <Player agent_3>: What are some common tasks that you perform at this location?.'
[Step 30]: '<Player agent_3> answered <Player agent_2>: Some common tasks I perform at this location include diagnosing car issues, conducting maintenance tasks, and repairing various parts of vehicles. It keeps me busy and helps keep the cars running smoothly..'
[Step 31]: '<Player agent_3> accused <Player agent_1> of being the spy.'
[Step 32]: '<Player agent_3> voted for <Player agent_1>: Yes.'
[Step 33]: '<Player agent_0> voted for <Player agent_1>: Yes.'
[Step 34]: '<Player agent_1> voted for <Player agent_1>: No.'
Not unanimous. Continue game.
[Step 35]: '<Player agent_2> voted for <Player agent_1>: No.'
[Step 36]: '<Player agent_1> asked <Player agent_2>: What type of customers do you usually encounter at this location?.'
[Step 37]: '<Player agent_2> answered <Player agent_1>: At this location, we typically encounter a variety of customers, from regular commuters needing fuel to travelers seeking assistance with their vehicles. It's important to provide quality service to everyone who comes through our doors..'
[Step 38]: '<Player agent_2> asked <Player agent_0>: What kind of tasks do you find yourself performing most frequently at this location?.'
[Step 39]: '<Player agent_0> answered <Player agent_2>: At this location, I find myself performing tasks related to maintaining and repairing vehicles. It's important to ensure that everything is in top condition for the customers who visit us..'
[Step 40]: '<Player agent_0> asked <Player agent_1>: What kind of training or qualifications do you need to work in our line of work?.'
[Step 41]: '<Player agent_1> answered <Player agent_0>: To work in our line of work, it's essential to have a strong understanding of automotive mechanics, problem-solving skills, and the ability to work efficiently and accurately under pressure. Additionally, having certifications or training in automotive repair and maintenance can be beneficial to excel in this field..'
Target agent was target of last dialogue. Sampling a random other last target.
[Step 42]: '<Player agent_1> asked <Player agent_2>: What kind of customers do you usually encounter at this location?.'
[Step 43]: '<Player agent_2> answered <Player agent_1>: At this location, we usually encounter a diverse range of customers, from regular commuters to people traveling long distances. It's important to provide excellent service to meet the different needs of everyone who visits us..'
[Step 49]: '<Player agent_3> asked <Player agent_2>: What do you find most challenging about working in this type of environment?.'
[Step 50]: '<Player agent_2> answered <Player agent_3>: One of the most challenging aspects of working in this type of environment is ensuring that all tasks are completed efficiently and accurately. It can be a fast-paced environment at times, so staying organized and prioritizing tasks effectively is crucial to keep everything running smoothly..'
[Step 51]: '<Player agent_2> accused <Player agent_3> of being the spy.'
[Step 52]: '<Player agent_2> voted for <Player agent_3>: No.'
[Step 53]: '<Player agent_0> voted for <Player agent_3>: No.'
[Step 54]: '<Player agent_1> voted for <Player agent_3>: No.'
Not unanimous. Continue game.
[Step 55]: '<Player agent_3> voted for <Player agent_3>: No.'
[Step 56]: '<Player agent_3> asked <Player agent_1>: What specific qualifications or certifications do you think are necessary to excel in a job like ours?.'
[Step 57]: '<Player agent_1> answered <Player agent_3>: Oh, to excel in a job like ours, having certifications in automotive repair and maintenance would definitely be beneficial. Additionally, having a strong understanding of automotive mechanics and problem-solving skills can really help in providing top-notch service to our customers..'
[Step 63]: '<Player agent_2> asked <Player agent_1>: What do you think is the most important skill to have in our line of work at this location?.'
[Step 64]: '<Player agent_1> answered <Player agent_2>: The most important skill to have in our line of work at this location is definitely problem-solving. Being able to quickly diagnose issues and come up with effective solutions is crucial for providing quality service to our customers and keeping operations running smoothly..'
        """
    ))