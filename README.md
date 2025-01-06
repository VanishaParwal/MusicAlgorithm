# MusicAlgorithm
## *Introduction*
It is an interactive music generation app powered by Python. Using data structures and algorithms, it creates unique melodies based on user inputs, such as mood, seed notes, and duration. The app visualizes the generation process, allowing users to understand and hear the steps behind creating a melody.

## *Features*
- *Interactive UI* using Streamlit.
- Generate melodies based on mood and user-defined parameters.
- Dynamic visualization of melody creation through animations.
- Export generated melodies as MIDI files.
- Educational: Illustrates how algorithms can be applied creatively.

## *Installation*
1. Clone this repository:
   bash
   git clone https://github.com/VanishaParwal/MusicAlgorithm
   cd melodify
   
2. Install the required dependencies:
   bash
   pip install -r requirements.txt
   
3. Run the application:
   bash
   streamlit run music.py
   

## *How It Works*
1. *User Input:*
   - Select mood: Happy, Sad, Energetic, Calm.
   - Define duration and optionally input a seed note.
2. *Algorithm Selection:*
   - Choose between graph traversal (e.g., DFS/BFS) or dynamic programming techniques.
3. *Melody Generation:*
   - Notes are generated step-by-step, visualized in real-time.
   - Musical transitions are represented as weighted edges in a graph.
4. *Playback and Export:*
   - Users can listen to the generated melody or export it as a MIDI file.

## *Code Snippet*
Below is a simplified version of the app.py script:

python
import streamlit as st
import networkx as nx
import random
from music21 import stream, note, midi

# Initialize Streamlit
st.title("Melodify: Algorithmic Music Composer")
st.sidebar.header("User Input")

# User Inputs
mood = st.sidebar.selectbox("Choose Mood", ["Happy", "Sad", "Energetic", "Calm"])
duration = st.sidebar.slider("Melody Duration (in seconds)", 5, 60, 15)
seed_note = st.sidebar.text_input("Seed Note (Optional)", "C")

# Create Note Graph
def create_note_graph():
    G = nx.DiGraph()
    notes = ["C", "D", "E", "F", "G", "A", "B"]
    for i in notes:
        for j in notes:
            G.add_edge(i, j, weight=random.uniform(0.1, 1))
    return G

note_graph = create_note_graph()

# Generate Melody
def generate_melody(graph, start_note, duration):
    melody = []
    current_note = start_note
    for _ in range(duration):
        melody.append(current_note)
        neighbors = list(graph.neighbors(current_note))
        current_note = random.choices(neighbors, weights=[graph[current_note][n]['weight'] for n in neighbors])[0]
    return melody

if st.button("Generate Melody"):
    melody = generate_melody(note_graph, seed_note, duration)
    st.write("Generated Melody:", melody)

    # Create a MIDI File
    midi_stream = stream.Stream()
    for n in melody:
        midi_stream.append(note.Note(n))

    midi_file = midi.translate.streamToMidiFile(midi_stream)
    midi_path = "melody.mid"
    midi_file.open(midi_path, 'wb')
    midi_file.write()
    midi_file.close()

    # Download Link
    with open(midi_path, "rb") as file:
        st.download_button(label="Download Melody as MIDI", data=file, file_name="melody.mid")

    st.audio(midi_path, format="audio/midi")

# Visualization
st.write("### Note Transition Graph")
st.graphviz_chart(nx.nx_agraph.to_agraph(note_graph))


## *UI Preview*
Below is a conceptual representation of the UI:

![alt text](<Screenshot 2025-01-06 101743.png>)


- *Top Section:* Title and description.
- *Sidebar:* User inputs for mood, duration, and seed notes.
- *Main Area:*
  - Visualization of the melody generation process.
  - Playback and download options.

## *How to Use*
1. Select your preferences in the sidebar.
2. Click the "Generate Melody" button to visualize and listen to the melody.
3. Export the generated melody as a MIDI file.

## *Future Enhancements*
- Add support for more moods and scales.
- Integrate deep learning models for melody generation.
- Provide more advanced visualization options.

## *License*
This project is licensed under the MIT License. Feel free to use, modify, and distribute it.

---

Enjoy composing with *Music*