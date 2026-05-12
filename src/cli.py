"""
Command line interface for MAGI Pipeline
"""

import sys
import click
from pathlib import Path

from .core.config import Config
from .pipeline.controller import MAGIPipeline


@click.command()
@click.option('--input', '-i', required=True, help='Input video file path')
@click.option('--output', '-o', required=True, help='Output video file path')
@click.option('--config', '-c', help='Configuration file path')
@click.option('--mode', '-m', default='3d-projector', 
              type=click.Choice(['3d-projector', 'vr-headset', '3d-tv', 'custom']),
              help='Output mode')
@click.option('--realtime', '-r', is_flag=True, help='Enable real-time processing')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(input, output, config, mode, realtime, verbose):
    """
    MAGI Video Pipeline - Convert videos to MAGI format
    
    Example usage:
    
    \b
    magipipeline -i input.mp4 -o output_magi.mp4 --mode 3d-projector
    magipipeline -i input_3d.mp4 -o output_magi.mp4 --realtime
    """
    
    try:
        # Load configuration
        if config:
            cfg = Config(config)
        else:
            cfg = Config()
        
        # Adjust logging level
        if verbose:
            cfg.logging.level = "DEBUG"
        
        # Create pipeline
        pipeline = MAGIPipeline(cfg)
        
        # Load input
        click.echo(f"Loading input video: {input}")
        if not pipeline.load_input(input):
            click.echo("Error: Could not load input video", err=True)
            sys.exit(1)
        
        # Display video information
        video_info = pipeline.get_processing_info()
        click.echo(f"Input: {video_info['input']['resolution']} @ {video_info['input']['fps']:.2f}fps")
        click.echo(f"3D: {video_info['input']['is_3d']} ({video_info['input']['3d_format']})")
        
        # Progress callback
        def progress_callback(progress, message):
            click.echo(f"[{progress:.0f}%] {message}")
        
        # Process video
        click.echo(f"Processing to: {output}")
        click.echo(f"Mode: {mode}")
        
        if realtime:
            success = pipeline.process_realtime(output)
        else:
            success = pipeline.process(output, progress_callback)
        
        if success:
            # Display processing information
            info = pipeline.get_processing_info()
            click.echo(f"\nProcessing complete!")
            click.echo(f"Processing time: {info.get('processing_time', 0):.2f} seconds")
            click.echo(f"Output: {output}")
        else:
            click.echo("Error: Processing failed", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@click.command()
@click.option('--input', '-i', required=True, help='Input video file path')
def analyze(input):
    """
    Analyze video file and display information
    """
    try:
        from .input import VideoInput
        
        click.echo(f"Analyzing: {input}")
        
        video_input = VideoInput()
        if not video_input.load(input):
            click.echo("Error: Could not load video", err=True)
            sys.exit(1)
        
        video_info = video_input.get_video_info()
        
        click.echo("\n=== Video Information ===")
        click.echo(f"Format: {video_info['format']}")
        click.echo(f"Duration: {video_info['duration']:.2f} seconds")
        click.echo(f"Size: {video_info['size'] / (1024*1024):.2f} MB")
        
        click.echo("\n=== Video Stream ===")
        click.echo(f"Codec: {video_info['video']['codec']}")
        click.echo(f"Resolution: {video_info['video']['width']}x{video_info['video']['height']}")
        click.echo(f"Frame Rate: {video_info['video']['fps']:.2f} fps")
        click.echo(f"Frame Count: {video_info['video']['frame_count']}")
        click.echo(f"Aspect Ratio: {video_info['video']['aspect_ratio']:.2f}")
        
        click.echo("\n=== Audio Stream ===")
        click.echo(f"Codec: {video_info['audio']['codec']}")
        click.echo(f"Sample Rate: {video_info['audio']['sample_rate']} Hz")
        click.echo(f"Channels: {video_info['audio']['channels']}")
        
        click.echo("\n=== 3D Information ===")
        click.echo(f"Format: {video_info['3d']['format']}")
        click.echo(f"Is 3D: {video_info['3d']['is_3d']}")
        
        # Get processing requirements
        requirements = video_input.get_processing_requirements(120, "3840x2160")
        
        click.echo("\n=== Processing Requirements ===")
        click.echo(f"Interpolation: {requirements['interpolation']['required']} "
                  f"(ratio: {requirements['interpolation']['ratio']})")
        click.echo(f"Upscaling: {requirements['upscaling']['required']} "
                  f"(ratio: {requirements['upscaling']['width_ratio']:.2f}x)")
        
        video_input.close()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.group()
def cli():
    """MAGI Video Pipeline CLI"""
    pass


cli.add_command(main, name='process')
cli.add_command(analyze, name='analyze')


if __name__ == '__main__':
    cli()