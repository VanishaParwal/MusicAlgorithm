import streamlit as st
import numpy as np
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import time
import random
import pygame.midi
import pygame.mixer
from midiutil.MidiFile import MIDIFile
import os

class MusicComposer:
    def __init__(self):
        self.notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        self.note_to_midi = {
            'C': 60, 'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'B': 71
        }
        self.octaves = [4, 5]
        self.durations = [0.25, 0.5, 1]
        self.graph = self._create_note_graph()
        
    def _create_note_graph(self):
        G = nx.DiGraph()
        for octave in self.octaves:
            for note in self.notes:
                G.add_node(f"{note}{octave}")
        
        for octave in self.octaves:
            for i, note in enumerate(self.notes):
                next_idx = (i + 1) % len(self.notes)
                prev_idx = (i - 1) % len(self.notes)
                
                G.add_edge(f"{note}{octave}", f"{self.notes[next_idx]}{octave}", weight=0.7)
                G.add_edge(f"{note}{octave}", f"{self.notes[prev_idx]}{octave}", weight=0.7)
                
                for other_octave in self.octaves:
                    if other_octave != octave:
                        G.add_edge(f"{note}{octave}", f"{note}{other_octave}", weight=0.3)
        
        return G

    def note_to_midi_number(self, note):
        note_name = note[0]
        octave = int(note[1])
        return self.note_to_midi[note_name] + (octave - 4) * 12

    def generate_melody(self, length, mood):
        melody = []
        weights = []
        current_note = random.choice([f"{note}{octave}" 
                                    for note in self.notes 
                                    for octave in self.octaves])
        
        mood_weights = {
            'happy': {'weight_mul': 1.2, 'duration_pref': 0.25},
            'sad': {'weight_mul': 0.8, 'duration_pref': 1},
            'energetic': {'weight_mul': 1.5, 'duration_pref': 0.25},
            'calm': {'weight_mul': 0.6, 'duration_pref': 0.5}
        }
        
        for _ in range(length):
            melody.append(current_note)
            neighbors = list(self.graph.neighbors(current_note))
            if not neighbors:
                break
                
            edge_weights = [self.graph[current_note][next_note]['weight'] * 
                        mood_weights[mood]['weight_mul']
                        for next_note in neighbors]
            
            total_weight = sum(edge_weights)
            if total_weight > 0:
                edge_weights = [w / total_weight for w in edge_weights]
            else:
                edge_weights = [1.0 / len(neighbors)] * len(neighbors)
            
            current_note = random.choices(neighbors, weights=edge_weights)[0]
            weights.append(random.random())
        
        return melody, weights

    def generate_melody_with_midi(self, length, mood, tempo):
        melody, weights = self.generate_melody(length, mood)
        
        # Create MIDI file
        midifile = MIDIFile(1)
        track = 0
        time_counter = 0
        channel = 0
        volume = 100
        
        # Convert tempo to microseconds per beat
        midifile.addTempo(track, time_counter, tempo)
        
        # Add notes to MIDI file
        for note in melody:
            midi_note = self.note_to_midi_number(note)
            duration = 1  # Quarter note
            midifile.addNote(track, channel, midi_note, time_counter, duration, volume)
            time_counter += 1
        
        # Save MIDI file
        midi_path = "temp_melody.mid"
        with open(midi_path, "wb") as f:
            midifile.writeFile(f)
        
        return melody, weights

def create_figure(melody=None, weights=None):
    fig = go.Figure()
    
    if melody and weights:
        x = list(range(len(melody)))
        y = [ord(note[0]) + float(note[1]) * 12 for note in melody]
        
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode='lines+markers',
                line=dict(color='blue'),
                name='Melody'
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=x,
                y=weights,
                mode='lines',
                line=dict(color='red'),
                name='Intensity'
            )
        )
    
    fig.update_layout(
        title="Melody Visualization",
        xaxis_title="Time",
        yaxis_title="Note Value",
        showlegend=True,
        height=500
    )
    
    return fig

def play_midi():
    try:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.load("temp_melody.mid")
        pygame.mixer.music.play()
    except Exception as e:
        st.error(f"Error playing audio: {str(e)}")

def stop_midi():
    try:
        if pygame.mixer.get_init() is not None and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
    except Exception as e:
        st.error(f"Error stopping audio: {str(e)}")

def main():
    st.set_page_config(page_title="Algorithmic Music Composer", layout="wide")
    
    # Initialize pygame
    if 'pygame_initialized' not in st.session_state:
        pygame.init()
        st.session_state.pygame_initialized = True
    
    st.title("🎵 Algorithmic Music Composer")
    
    composer = MusicComposer()
    
    with st.sidebar:
        st.header("Controls")
        mood = st.selectbox("Select Mood", ['happy', 'sad', 'energetic', 'calm'])
        length = st.slider("Melody Length", 8, 32, 16)
        tempo = st.slider("Tempo (BPM)", 60, 180, 120)
        
        if st.button("Generate New Melody"):
            stop_midi()  # Stop any playing music
            st.session_state.melody, st.session_state.weights = composer.generate_melody_with_midi(
                length, mood, tempo
            )
            st.session_state.current_pos = 0
            st.session_state.playing = False
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        chart_placeholder = st.empty()
        
        if 'melody' not in st.session_state:
            st.session_state.melody, st.session_state.weights = composer.generate_melody_with_midi(
                length, mood, tempo
            )
            st.session_state.current_pos = 0
            st.session_state.playing = False
        
        # Audio and visualization controls
        audio_col1, audio_col2, audio_col3 = st.columns(3)
        with audio_col1:
            play_visual = st.button("▶ Play Animation")
        with audio_col2:
            play_audio = st.button("🔊 Play Melody")
        with audio_col3:
            stop_audio = st.button("⏹ Stop")
        
        if play_audio:
            play_midi()
        if stop_audio:
            stop_midi()
        
        if play_visual:
            st.session_state.playing = True
            st.session_state.current_pos = 0
        
        if st.session_state.playing:
            while st.session_state.current_pos <= len(st.session_state.melody):
                current_melody = st.session_state.melody[:st.session_state.current_pos]
                current_weights = st.session_state.weights[:st.session_state.current_pos]
                
                fig = create_figure(current_melody, current_weights)
                chart_placeholder.plotly_chart(fig, use_container_width=True)
                
                st.session_state.current_pos += 1
                time.sleep(0.1)
            
            st.session_state.playing = False
        else:
            fig = create_figure(st.session_state.melody, st.session_state.weights)
            chart_placeholder.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Current Melody")
        st.write("Notes:", ", ".join(st.session_state.melody))
        
        st.subheader("Note Transitions")
        G = composer.graph
        pos = nx.spring_layout(G)
        
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        
        fig_graph = go.Figure()
        fig_graph.add_trace(
            go.Scatter(
                x=edge_x, y=edge_y,
                mode='lines',
                line=dict(color='gray', width=0.5),
                hoverinfo='none'
            )
        )
        fig_graph.add_trace(
            go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(size=10),
                text=list(G.nodes()),
                textposition='top center'
            )
        )
        
        fig_graph.update_layout(
            showlegend=False,
            height=400,
            title="Note Graph Structure"
        )
        st.plotly_chart(fig_graph, use_container_width=True)

    # Cleanup on app reload
    if os.path.exists("Romantic-Piano.mid"):
        try:
            os.remove("Romantic-Piano.mid")
        except:
            pass

if __name__ == "__main__":
    main()