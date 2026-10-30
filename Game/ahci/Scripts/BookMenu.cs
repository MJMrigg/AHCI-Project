using Godot;

public partial class BookMenu : Control
{
	// Instructions based on audio/keyboard mode and (un)translated mode
	[Export(PropertyHint.MultilineText)]
	public string UntranslatedSoundInstructions = "\n\nSæ \"brœs\" tra clænx thës ovra'lei";
	[Export(PropertyHint.MultilineText)]
	public string UntranslatedVocalInstructions = "\n\nSæ \"brœs\" tra clænx thës ovra'lei";
	[Export(PropertyHint.MultilineText)]
	public string UntranslatedKeyboardInstructions = "\n\nPrš \"ɘ\" tra chœ̆l thîs uvea'lea";
	[Export(PropertyHint.MultilineText)]
	public string TranslatedSoundInstructions = "\n\nSay \"close\" to close this overlay";
	[Export(PropertyHint.MultilineText)]
	public string TranslatedVocalInstructions = "\n\nSay \"close\" to close this overlay";
	[Export(PropertyHint.MultilineText)]
	public string TranslatedKeyboardInstructions = "\n\nPress \"e\" to close this overlay";

	// Helper variables for getting the (un)translated versions based on the audio mode
	public string UntranslatedInstructions {
		get {
			switch(GameMaster.Instance.Mode)
			{
				case 0:
					return UntranslatedKeyboardInstructions;
				case 1:
					return UntranslatedVocalInstructions;
				case 2:
					return UntranslatedSoundInstructions;
				default:
					return "";
			}
		}
	}

	public string TranslatedInstructions {
		get {
			switch(GameMaster.Instance.Mode)
			{
				case 0:
					return TranslatedKeyboardInstructions;
				case 1:
					return TranslatedVocalInstructions;
				case 2:
					return TranslatedSoundInstructions;
				default:
					return "";
			}
		}
	}

	private Label _label;
	private Book _activeBook;
	[Signal]
	public delegate void ReadEventHandler(int Book);

	public override void _Ready()
	{
		base._Ready();
		_label = GetNode<Label>("ColorRect/Label");
	}

	public override void _UnhandledInput(InputEvent @event)
	{
		base._UnhandledInput(@event);
		// Handles user input for translating book
		if (@event.IsActionPressed("Translate"))
		{
			Translate();
		}
	}

	public void Translate()
	{
		GD.Print("TEST1");
		if(_activeBook == null)
		{
			return;
		}
		GD.Print("TEST2");
		_label.Text = _activeBook.Translated + TranslatedInstructions;
		GameMaster.Instance.Book = _activeBook.BookNumber;
		EmitSignal(SignalName.Read, _activeBook.BookNumber);
	}

	public bool IsOpen(Book book)
	{
		return IsInstanceValid(_activeBook) && _activeBook == book;
	}

	public void Open(Book book)
	{
		_activeBook = book;
		Visible = true;
		_label.Text = _activeBook.Untranslated + UntranslatedInstructions;
	}

	public void Close()
	{
		_activeBook = null;
		Visible = false;
		_label.Text = "This is some test text.";
	}
}
