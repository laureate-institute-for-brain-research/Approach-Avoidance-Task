package 
{
	import flash.display.StageDisplayState;
	import flash.display.Stage;
	import flash.desktop.NativeApplication;
	import fl.controls.TextInput;
	
	import flash.display.MovieClip;
	import flash.geom.Matrix;
	import flash.events.*;
	import flash.utils.*;
	import flash.filesystem.*;
	import flash.net.FileFilter;
	
	import flash.media.Sound;
	import flash.media.SoundMixer;
	import flash.filesystem.File;
	import flash.display.Loader;
	import flash.display.LoaderInfo;
    import flash.display.Sprite;
    import flash.net.URLRequest;
	
	import flash.display.Sprite;
	import flash.text.TextField;
	import flash.text.TextFieldAutoSize;
	import flash.text.TextFormat;

	public class engine extends MovieClip 
	{
		public var screenNum:int = 1;
		public var timer:Timer;
		public var trialNum:int = 1;
		
		public var fileToOpen:File = new File();
		public var fileData:String;
		public var ID:String;
		
		public var fileContentsSplit:Array; 
		public var numLines:uint;
		public var fileContentsSplitItem : Array;
		public var fileContentsSplitParameters: Array;
		
		public var fluidMultiplier: Number;
		public var fluidHeight:Number = 129;
		public var configStartPoint:int;
		public var totalTrials:int;
		public var configLReward:int;
		public var configRReward:int;
		public var configLImage:String;
		public var configLSound:String;
		public var configRImage:String;
		public var configRSound:String;
		public var configITD:int;
		public var configDecisionD:int;
		public var configStimD:int;
		public var configPointsD:int;
		public var configLAversive:int;
		
		public var posImage:String;
		public var posSound:String;
		public var negImage:String;
		public var negSound:String;
		public var outImage:String;
		public var negSide:String;
		
		public var stimMC:MovieClip;
		public var imageFile:File;
		public var soundFile:File;
		public var sound:Sound;
		
		public var down1:int = 0;
		public var down2:int = 0;
		public var down3:int = 0;
		public var down4:int = 0;
		public var down5:int = 0;
		public var down6:int = 0;
		public var down7:int = 0;
		public var down8:int = 0;
		public var down9:int = 0;
		public var button:int = 0;
		public var locked:int = 0;
		
		public var responseNum:int = 0;
		public var responseNumstr:String;
		public var oscillations:int = 0;
		public var paradigmStartTime:int=0;
		public var startTime:int=0;
		public var initialRT:int=0;
		public var totalRT:int=0;
		public var outputData:String;
		public var manX:Number;
		public var squareX:Number;
		
		public var pointsTrial:int = 0;
		public var pointsTotal:int = 0;
		public var pointsTotalb:int = 0;
		public var pointsOther:int = 0;

		public var logFile:File;
		public var logFileStream:FileStream = new FileStream ();
		public var logFileEvents:File;
		public var logFileEventsStream:FileStream = new FileStream ();
		public var operatorName:String;
		public var subjectID:String;
		public var timeStamp:Date = new Date();
		public var fileDate:String;
		public var folderToOpen:File = new File ();
			
		function engine () 
		{
			setUpGUI();
			fileOpen();
		}
		
		function setUpGUI():void
		{
			stage.displayState = StageDisplayState.FULL_SCREEN_INTERACTIVE;
			stage.frameRate = 1000;
			stage.addEventListener (KeyboardEvent.KEY_DOWN, keyDownHandler);
			stage.addEventListener (KeyboardEvent.KEY_UP, keyUpHandler);
			
			firstScreen.visible = true;
			selectCSV.visible = false;
			pauseScreen.visible = false;
			theEnd.visible = false;
			lastScreen.visible = false;
			manX = man.x;
			squareX = square.x;
			buildDecision(false);
		}
		
		function folderOpen ():void
		{
			folderToOpen.browseForDirectory("Select a directory");
			folderToOpen.addEventListener(Event.SELECT, dirSelected);
		}
		
		function dirSelected(event:Event):void {
				trace(folderToOpen.nativePath);
			}
			
			
		function fileOpen ():void 
		{
			if (selectCSV.visible == true)
			{
				selectCSV.visible = false;
			}
			
			try 
			{
				var txtFilter:FileFilter = new FileFilter("Text", "*.csv"); //;*.txt;*.xml"
				fileToOpen.browseForOpen("Open", [txtFilter]);
				fileToOpen.addEventListener(Event.SELECT, fileSelected);
				fileToOpen.addEventListener(Event.CANCEL, fileOpenError);
			}
			
			catch (error:Error)
			{
				trace("Failed:", error.message);
			}
		}
		
		function fileOpenError (event:Event):void
		{
			selectCSV.visible = true;
			selectCSV.selectCSVbtn.addEventListener(MouseEvent.CLICK, fileOpenAgain);
		} 
		
		function fileOpenAgain (event:Event):void
		{
			fileOpen ();
		}
		
		function fileSelected (event:Event):void 
		{
			var stream:FileStream = new FileStream();
			stream.open(fileToOpen, FileMode.READ);
			fileData = stream.readUTFBytes(stream.bytesAvailable);
			
			parseCSV(fileData);
			folderOpen ();
		}
		
		function parseCSV (fileContents:String):void 
		{
			var splitTerms:RegExp = /\r\n?/;
			fileContentsSplit = fileContents.split(splitTerms); 
			numLines = fileContentsSplit.length;
			
			//general parameters
			fileContentsSplitParameters = fileContentsSplit[1].split(",");
			fluidMultiplier = fileContentsSplitParameters[0];
			trace("fluidMultiplier: " + fluidMultiplier);
			
			//get trial count
			trace("   ");
			
			totalTrials = (numLines-3); //-3 because we ignore the first 3 lines
			
			trace("numlines - "+ numLines)
			trace("initially there are "+ totalTrials+" total trials")
			
			var blankLines:int;
			
			for (var i:int=3; i < numLines; i++)
			{
				trace("loop is at array line "+i+" or csv line "+(i+1)+" or trial "+(i-2))
				fileContentsSplitItem = fileContentsSplit[i].split(",");
				
				if (fileContentsSplitItem.length < 2)
				{
					totalTrials--;
					blankLines++;
					trace("blank "+" - "+fileContentsSplitItem)
					//remeber the first line is 0, so a 75 line file will go to 74 here (counting 0)
				} 
			}
			
			
			trace("now there are " + totalTrials + " actual trials ("+numLines+" array lines - first "+3+" skipped - "+blankLines+" blank lines)"); 
			trace("   ");
				  
			updateVars();
			clearDecisionVars ();
			
			//program starts when user presses "s"
		}
			
		function startTimer ():void
		{
			flexTimer(configITD);
			ID = firstScreen.enteridtxt.text;
			createLogFileEvents();
			createLogFile();
		}
		
		function updateVars ():void 
		{
			//splits into each item in the array, start at trialnum+2 to skip the first 2 lines
			fileContentsSplitItem = fileContentsSplit[(trialNum+2)].split(",");
			
			//trace("fileContentsSplitItem range: 0 - " + (fileContentsSplitItem.length-1))
			
			/*
			
			this is how you extract variables for each part
			
			0 run #,
			1 left reward,
			2 right reward,
			
			3 stim left image,
			4 stim left sound,
			5 stim right image,
			6 stim right sound,
			
			7 itd (sec),
			8 decision (sec),
			9 stim  (sec),
			10 points (sec),
			
			11 -4,
			12 -3,
			13 -2,
			14 -1,
			15 0,
			16 1,
			17 2,
			18 3,
			19 4,
			
			20 startPoint,
			21 left is aversive
			
			config = fileContentsSplitItem[0];
			
			*/
			
			configLReward = fileContentsSplitItem[1];
			configRReward = fileContentsSplitItem[2];
			
			configLImage = fileContentsSplitItem[3];
			configLSound = fileContentsSplitItem[4];
			configRImage = fileContentsSplitItem[5];
			configRSound = fileContentsSplitItem[6];
			
			configITD = fileContentsSplitItem[7];
			configDecisionD = fileContentsSplitItem[8];
			configStimD = fileContentsSplitItem[9];
			configPointsD = fileContentsSplitItem[10];
			
			configStartPoint = fileContentsSplitItem[20];
			configLAversive = fileContentsSplitItem[21];
						
			thermLeft.fluid.height = fluidMultiplier * configLReward;
			thermRight.fluid.height = fluidMultiplier * configRReward;
			
			trace("configStartPoint " + configStartPoint);
			
		}
		

		
		function flexTimer (timerRepeat:int):void
		{
			if (trialNum >= totalTrials && screenNum == 1)
			{
				buildLastScreen ();
			} else
			{
				//var timerRepeatBig:int = timerRepeat*20;
				timer = new Timer(1000, timerRepeat);
				timer.addEventListener (TimerEvent.TIMER, timerHandler);
				timer.addEventListener (TimerEvent.TIMER_COMPLETE, timerComplete);
				timer.start();
				//trace("TIMER " + screenNum + " START -----");
			}
		}
		
		function timerHandler (e:TimerEvent):void 
		{
			trace(timer.currentCount);
		}
		
		function timerComplete (e:TimerEvent):void 
		{
			//trace("TIMER " + screenNum + " END -----");
			
			timer.stop();
			timer.reset();
			screenSwitchboard();
		}
		
		function screenSwitchboard ():void 
		{
			if (screenNum == 4) 
			{ 	
				screenNum = 1;
			} 
			else {screenNum++;}
			
			switch (screenNum)
			{
				//itd
				case 1:
				trace("  ");
				//trace("=================================================");
				trace("trial " +trialNum);
				
				screen.visible = true;
				fixationMC.visible = true;
				flexTimer (configITD);
				logEventData ("program_fixation_screen", null, null);
				break;
				
				//decision
				case 2:
				trace("trial " +trialNum);
				fixationMC.visible = false;
				buildDecision(true);
				flexTimer (configDecisionD);
				break;
				
				//stim
				case 3:
				buildDecision(false);
				buildStimMC();
				flexTimer (configStimD);
				break;
				
				//points
				case 4:
				screen.visible = false;
				removeChild (stimMC);
				buildPoints();
				logData();
				flexTimer (configPointsD);
				if (trialNum !== totalTrials)
				{
					trialNum++;
					updateVars();
					
				}
				break;
			}
		}
		
		function buildDecision (show:Boolean):void
		{
			if (show == true)
			{
				clearDecisionVars();
				line.visible = true;
				responseNum = configStartPoint;
				man.visible = true;
				square.visible = false;
				man.x = manX + (configStartPoint*63.2);
				square.x = squareX + (configStartPoint*63.2);
				thermLeft.visible = true;
				thermRight.visible = true;
				logEventData ("trial", String(trialNum), null);
				logEventData ("program_decision_screen", null, null);
				
				if (configLAversive == 1)
				{
					sunL.visible = false;
					cloudsL.visible = true;
					
					sunR.visible = true;
					cloudsR.visible = false;
					
					posImage = configRImage;
					posSound = configRSound;
					negImage = configLImage;
					negSound = configLSound;
					negSide = "L";
					
				} else if (configLAversive == 0)
				{
					sunL.visible = true;
					cloudsL.visible = false;

					sunR.visible = false;
					cloudsR.visible = true;
					
					posImage = configLImage;
					posSound = configLSound;
					negImage = configRImage;
					negSound = configRSound;
					negSide = "R";
					
				} else if (configLAversive == 3)
				{
					sunL.visible = true;
					cloudsL.visible = false;
					
					sunR.visible = true;
					cloudsR.visible = false;
					
					posImage = configLImage;
					posSound = configLSound;
					negImage = configRImage;
					negSound = configRSound;
					negSide = "L";
					
				} 				
				
			} else if (show == false)
			{
				line.visible = false;
				man.visible = false;
				square.visible = false;
				thermLeft.visible = false;
				thermRight.visible = false;
				sunL.visible = false;
				cloudsL.visible = false;
				sunR.visible = false;
				cloudsR.visible = false;
			}
			
			startTime = getTimer();
			
		}
		
		function clearDecisionVars ():void
		{
			button = 0;
			oscillations = 0;
			initialRT=0;
			totalRT=0;
			locked = 0;
			
		}
		
		function buildStimMC ():void
		{
			stimMC = new MovieClip();
			addChild(stimMC);
			stimMC.name = "stimMC";
	
			if (fileContentsSplitItem[(15 + responseNum)] == "L")
			{
				fileLoad(configLImage, configLSound);
				
				outImage = configLImage;
				
				trace("loading: "+ configLImage + " "+ configLSound);
			} else if (fileContentsSplitItem[(15 + responseNum)] == "R")
			{
				fileLoad(configRImage, configRSound);
				
				outImage = configRImage;
				
				trace("loading: "+ configRImage + " "+ configRSound);
			}
			
			stimMC.x = 138;
			stimMC.y = 116;
			
			//logEventData ("program_stimulus_screen", null, null);
		}

		function fileLoad (imagePath:String, soundPath:String)
		{
			if (imagePath !== null)
			{
				try 
				{
					imageFile = File.applicationDirectory.resolvePath(imagePath); //"images/" + "1.png";
					imageFile.canonicalize();
					var image:Loader = new Loader();
					var imageRequest:URLRequest = new URLRequest(imageFile.url);
					
					//image.contentLoaderInfo.addEventListener(Event.COMPLETE, addStimImage);
					image.load(imageRequest);
					stimMC.addChild (image);
					//trace(imagePath.url);
					
					logEventData ("program_stimulus_image", imagePath, null);
				}
				catch (error:Error)
				{
					trace("Failed:", error.message);
				}
			
			}
			
			if (soundPath !== null)
			{
				soundFile = File.applicationDirectory.resolvePath(soundPath); //"images/" + "1.wav"
				soundFile.canonicalize();
				sound = new Sound();
				var soundRequest:URLRequest = new URLRequest(soundFile.url);
				sound.load(soundRequest);
				sound.play();
				//trace(soundPath.url);
				
				logEventData ("program_stimulus_sound", null, soundPath);
			}
		}
		
		function buildPoints ():void
		{
			//stops the stim sound
			SoundMixer.stopAll(); 
			
			trace("configLReward: "+configLReward);
			trace("configRReward: "+configRReward);
			
			logEventData ("program_points_screen", null, null);
			
			//sound picker
			if (configLReward > configRReward && fileContentsSplitItem[(15 + responseNum)] == "L") 
			{
				//trace("1 configLReward > configRReward && fileContentsSplitItem[(15 + responseNum)] == L   big");
				fileLoad(null, "sounds/reward/bigReward.mp3");	
			}else if (configLReward > configRReward && fileContentsSplitItem[(15 + responseNum)] == "R")
			{
				//trace("2 configLReward > configRReward && fileContentsSplitItem[(15 + responseNum)] == R   small");
				fileLoad(null, "sounds/reward/smallReward.mp3");
			}else if (configLReward < configRReward && fileContentsSplitItem[(15 + responseNum)] == "L")
			{
				//trace("3 configLReward < configRReward && fileContentsSplitItem[(15 + responseNum)] == L   big");
				fileLoad(null, "sounds/reward/smallReward.mp3");
			}else if (configLReward < configRReward && fileContentsSplitItem[(15 + responseNum)] == "R")
			{
				//trace("4 configLReward < configRReward && fileContentsSplitItem[(15 + responseNum)] == R   big");
				fileLoad(null, "sounds/reward/bigReward.mp3");
			}else if (configLReward == configRReward)
			{
				//trace("5 configLReward == configRReward");
				fileLoad(null, "sounds/reward/smallReward.mp3");
			}
			
			//calculate points
			if (fileContentsSplitItem[(15 + responseNum)] == "L")
			{
				pointsTrial = fileContentsSplitItem[1];
				pointsOther = fileContentsSplitItem[2];
				trace("outcome L: reward "+ fileContentsSplitItem[1] +" col in CSV: "+ String(Number(15 + responseNum)) + " dir in CSV: " + fileContentsSplitItem[(15 + responseNum)] + " configLAversive:" + configLAversive);
			} else if (fileContentsSplitItem[(15 + responseNum)] == "R")
			{
				pointsTrial = fileContentsSplitItem[2];
				pointsOther = fileContentsSplitItem[1];
				trace("outcome R: reward "+ fileContentsSplitItem[2] +" col in CSV: "+ String(Number(15 + responseNum)) +" dir in CSV: "+ fileContentsSplitItem[(15 + responseNum)] + " configLAversive:" + configLAversive);
			}
			
			trace("responseNum buildPoints: "+responseNum);
			
			//update total
			pointsTotal += pointsTrial;
			
			//display points
			pointsTrialText.text=String(pointsTrial);
			trace("responseNum pointsTrial: "+pointsTrial);
			pointsTotalText.text=String(pointsTotal);
			trace("responseNum pointsTotal: "+pointsTotal);
		}

		function keyDownHandler (event:KeyboardEvent):void 
		{
			
			var currentLogTime						:Date		= new Date();
			
			var timeStamp						:String 	= (	currentLogTime.getHours()			+"."+ 
																	currentLogTime.getMinutes()			+"."+
																	currentLogTime.getSeconds()			+"."+
																	currentLogTime.getMilliseconds()				);
			
			var code:uint = event.keyCode;
			
			trace("oscillations "+oscillations);
			
			switch (code) 
			{
				//case 49 ://1
				//case 82 ://r
				//case 71 ://g
				//case 66 ://b
				//case 89 ://y
				case 49 ://1
					if (screenNum == 2 && down6 !== 1 && responseNum > -4)
					{
						if (locked == 0)
						{
							man.x -= 63.2;
							square.x -= 63.2;
							responseNum -= 1;
						
							if (button !==1)
							{
								oscillations++;
							} 
							if (button ==0)
							{
								initialRT = getTimer();
								initialRT = initialRT-startTime;
								trace("initialRT: "+ initialRT);
							}
						}
						logEventData ("response_L", String(responseNum), null);
					}
							
					
					button = 1;
					down6 = 1;
					break;
								
				case 37 ://left
					if (screenNum == 2 && down1 !== 1 && responseNum > -4)
					{
						if (locked == 0)
						{
							man.x -= 63.2;
							square.x -= 63.2;
							responseNum -= 1;
						
							if (button !==1)
							{
								oscillations++;
							} 
							if (button ==0)
							{
								initialRT = getTimer();
								initialRT = initialRT-startTime;
								trace("initialRT: "+ initialRT);
							}
						}
						logEventData ("response_L", String(responseNum), null);
					}
								
					button = 1;
					down1 = 1;
					break;
					
				//case 50 ://2
				case 51 ://3
					if (screenNum == 2 && down7 !== 1 && responseNum < 4)
					{
						if (locked == 0)
						{
							man.x += 63.2;
							square.x += 63.2;
							responseNum += 1;
						
							if (button !==2)
							{
								oscillations ++;
							} 
							if (button == 0)
							{
								initialRT = getTimer();
								initialRT = initialRT-startTime;
								trace("initialRT: "+ initialRT);
							}
						}
						logEventData ("response_R", String(responseNum), null);
					}		
					
					down7 = 1;
					button = 2;
					break;

				case 39 ://right
					if (screenNum == 2 && down2 !== 1 && responseNum < 4)
					{
						if (locked == 0)
						{
							man.x += 63.2;
							square.x += 63.2;
							responseNum += 1;
						
							if (button !==2)
							{
								oscillations ++;
							} 
							if (button == 0)
							{
								initialRT = getTimer();
								initialRT = initialRT-startTime;
								trace("initialRT: "+ initialRT);
							}
						}
						logEventData ("response_R", String(responseNum), null);
					}
					
					down2 = 1;
					button = 2;
					break;
					
				case 66 ://b, hopefully left on response box
					if (screenNum == 2 && down4 !== 1 && responseNum > -4)
					{
						if (locked == 0)
						{
							man.x -= 63.2;
							square.x -= 63.2;
							responseNum -= 1;
						
							if (button !==1)
							{
								oscillations++;
							} 
							if (button ==0)
							{
								initialRT = getTimer();
								initialRT = initialRT-startTime;
								trace("initialRT: "+ initialRT);
							}
						}
						logEventData ("response_L", String(responseNum), null);
					}
						
					button = 1;
					down4 = 1;
					break;
				
				//case 50 ://2
				//case 39 ://right
				case 82 ://r, hopefully right on response box (middle button)
					if (screenNum == 2 && down5 !== 1 && responseNum < 4)
					{
						if (locked == 0)
						{
							man.x += 63.2;
							square.x += 63.2;
							responseNum += 1;
						
							if (button !==2)
							{
								oscillations ++;
							} 
							if (button == 0)
							{
								initialRT = getTimer();
								initialRT = initialRT-startTime;
								trace("initialRT: "+ initialRT);
							}
						}
						logEventData ("response_R", String(responseNum), null);
					}
					
					down5 = 1;
					button = 2;
					break;
					
				//case 51 ://3
				case 38 ://up
					if (screenNum == 2 && down3 !== 1)
					{
						//man.x = manX;
						//responseNum = 0;
						locked = 1;
						square.visible = true;
						//ends trial and moves on
						//timer.stop();
						//timer.reset();
						
						totalRT = getTimer();
						totalRT = totalRT-startTime;
						trace("totalRT: "+ totalRT);
						//screenSwitchboard();
						
					}
					logEventData ("response_Lock", String(responseNum), null);
					
					down9 = 1;
					button = 3;
					break;
					
				case 40 ://down
					if (screenNum == 2 && down9 !== 1)
					{
						//man.x = manX;
						//responseNum = 0;
						locked = 1;
						square.visible = true;
						//ends trial and moves on
						//timer.stop();
						//timer.reset();
						
						totalRT = getTimer();
						totalRT = totalRT-startTime;
						trace("totalRT: "+ totalRT);
						//screenSwitchboard();
						
					}
					
					logEventData ("response_Lock", String(responseNum), null);
					
					down9 = 1;
					button = 3;
					break;

				//case 51 ://3
				case 50 ://2
					if (screenNum == 2 && down8 !== 1)
					{
						//man.x = manX;
						//responseNum = 0;
						locked = 1;
						square.visible = true;
						//ends trial and moves on
						//timer.stop();
						//timer.reset();
						
						totalRT = getTimer();
						totalRT = totalRT-startTime;
						trace("totalRT: "+ totalRT);
						//screenSwitchboard();
					logEventData ("response_Lock", String(responseNum), null);
					
					down8 = 1;
					button = 3;
					}
					

					break;
					
				case 83 ://s
					if (firstScreen.visible==true)
					{
						startTimer ();
						firstScreen.visible=false;
						paradigmStartTime = getTimer();	
					}
					
					logEventData ("program_start", null, null);
					
					break;
				
				case 81 ://q
					if (event.shiftKey == true) //shift+q
					{
						logEventData ("program_exit", null, null);
						exitApp();
					}
					break;
				
				case 80 ://p
					if (pauseScreen.visible == false)
					{
						timer.reset();
						SoundMixer.stopAll();			
						pauseScreen.visible = true;
						logEventData ("program_pause", null, null);
					} else if (pauseScreen.visible == true)
					{
						timer.start();
						pauseScreen.visible = false;
						logEventData ("program_unpause", null, null)
					}
					break;
			}
			
			//trace(timeStamp + "," + trialNum + "," + button + "," + responseNum + "," + screenNum);
			trace("responseNum keyDownHandler: "+responseNum);
			
			//http://livedocs.adobe.com/flash/9.0/main/wwhelp/wwhimpl/common/html/wwhelp.htm?context=LiveDocs_Parts&file=00001136.html
		}
		
		function keyUpHandler (event:KeyboardEvent):void 
		{
			
			var code:uint = event.keyCode;
			
			switch (code) 
			{	
				//case 49 ://1
				case 49 ://1
					down6 = 0;
					break;
				case 37 ://left
					down1 = 0;
					break;
				//case 50 ://2
				case 39 ://right
					down2 = 0;
					break;
				case 51 ://3
					down7 = 0;
					break;
				//case 51 ://3
				case 38 ://up
					down3 = 0;
					break;
				case 66 ://left
					down4 = 0;
					break;
				//case 50 ://2
				case 82 ://right
					down5 = 0;
					break;
				case 50 ://2
					down8 = 0;
					break;
				case 40 ://down
					down9 = 0;
					break;
			}
			
		}
		
 		function buildLastScreen ():void
		{
			theEnd.visible = true;
			
			var endTimer:Timer;
			endTimer = new Timer(500,4);
			endTimer.addEventListener (TimerEvent.TIMER_COMPLETE, buildAwardsScreen);
			endTimer.start();
			
			logEventData ("program_end_screen", null, null);
		}
		
		function buildAwardsScreen (e:TimerEvent):void
		{
			theEnd.visible = false;
			lastScreen.visible = true;
			
			lastScreen.thermFinal.thermFinalLiquid.height = 0;
			
			fileLoad(null, "sounds/reward/lastScreen.wav");
			
			var thermTimer:Timer;
			thermTimer = new Timer(1.67,600);
			thermTimer.addEventListener (TimerEvent.TIMER, thermTimerHandler);
			thermTimer.start();
			
			lastScreen.firstP.visible = false;
			lastScreen.second.visible = false;
			lastScreen.third.visible = false;
			lastScreen.mention.visible = false;
			
			logEventData ("program_awards_screen", null, null);
		}
		
		function thermTimerHandler (e:TimerEvent):void
		{
			if (lastScreen.thermFinal.thermFinalLiquid.height < pointsTotal*2)
			{
				lastScreen.thermFinal.thermFinalLiquid.height += 1;
				trace("height: "+lastScreen.thermFinal.thermFinalLiquid.height);
			} 
			
			else if (lastScreen.thermFinal.thermFinalLiquid.height > pointsTotal*1.99)
			{
				if (pointsTotal > 300)
				{
					lastScreen.firstP.visible = true;
				}
				
				else if (pointsTotal > 224 && pointsTotal < 300)
				{
					lastScreen.firstP.visible = true;
				}
				
				else if (pointsTotal > 149 && pointsTotal < 225)
				{
					lastScreen.second.visible = true;
				}
				
				else if (pointsTotal > 74 && pointsTotal < 150)
				{
					lastScreen.third.visible = true;
				}
				
				else if (pointsTotal < 75)
				{
					lastScreen.mention.visible = true;
				}
			}
		}
		
//		function thermTimerHandler (e:TimerEvent):void 
//		{
		//	if (lastScreen.thermFinal.thermFinalLiquid.height < pointsTotal*6)
			//{
				//lastScreen.thermFinal.thermFinalLiquid.height += 1;
			//} else if (lastScreen.thermFinal.thermFinalLiquid.height > pointsTotal*4.65)
			//{
				//if (pointsTotal > 89 && pointsTotal < 130)
				//{
				//	lastScreen.firstP.visible = true;
				//}else if (pointsTotal > 59 && pointsTotal < 90)
				//{
					//lastScreen.second.visible = true;
				//}else if (pointsTotal > 29 && pointsTotal < 60)
				//{
					//lastScreen.third.visible = true;
				//}else if (pointsTotal < 30)
				//{
					//lastScreen.mention.visible = true;
				//}
			//}
		//}
		
		function createLogFile():void 
		{
			/*
			{
			
			subjectID	= String	(create_page.subjectID_txt.text);
			operatorName = String	(create_page.operatorName_txt.text);
			
			var logFile:File;

			if (subjectID == "Subject ID") 
			{
				logFile	= File.desktopDirectory.resolvePath( "Effort Task Logs/" + "time " + [fileTime] + "  " + [fileDate] + ".csv" );
			} else {
				logFile	= File.desktopDirectory.resolvePath( "Effort Task Logs/" + [subjectID] + "  " + [fileDate] + ".csv" );
			}
			
			}
			*/
		

			logFile	= folderToOpen.resolvePath( "AACData/" + [ID] + "AAC" + "_" + [fileDate] + ".csv" );
			
			logFileStream.open(logFile, FileMode.APPEND);
			
			logFileStream.writeMultiByte ( 	"PtsOther"	+ "," +
											"Negative Image Side (1=L and 0=R)"	+ "," +
											"StartPos (starting position of the avatar)"	+ "," +
											"EndPos (end position of the avatar)"	+ "," +
											"InitialRT (reaction time for initial response)"	+ "," +
											"TotalRT (total time until they lock in response will be 4 seconds if they do not lock in)"	+ "," +
											"OutcomePts (Pts received)"	+ "," +
											"OutcomeImage (image shown)"	+ "," +
											"Piname (name of positive image file)"	+ "," +
											"Niname (name of negative image file)"	+ "," +
											"Paname (name of positive audio file)"	+ "," +
											"Naname (name of negative audio file)"	+ "," +
											"Oscillations (# made opposite movement from last)"	+ "\n"
											, File.systemCharset);
		}
		
		function createLogFileEvents():void 
		{
			fileDate = ((timeStamp.getMonth()+1) +""+ timeStamp.getDate() +""+ timeStamp.getFullYear() +"at"+ timeStamp.getHours()+"-"+ timeStamp.getMinutes());
			
			logFileEvents = folderToOpen.resolvePath( "AACData/" + [ID] + "AAC" + "_" + [fileDate] + "events.csv" );
			
			logFileEventsStream.open (logFileEvents, FileMode.APPEND);
			
			logFileEventsStream.writeMultiByte ( "Time"	+ "," +"Event" + "," +"Image" + "," + "Sound" + "\n", File.systemCharset);
		}
		
		function logData ():void 
		{
			trace("theoretically logging data");
			
			if (totalRT == 0)
			{
				totalRT = configDecisionD*1000;
			}
			
			outputData = pointsOther + "," +
							negSide	+ "," +
							configStartPoint + "," +
							responseNum	+ "," +
							initialRT	+ "," +
							totalRT + "," +
							pointsTrial	+ "," +
							outImage + "," +
							posImage + "," +
							negImage + "," +
							posSound + "," +
							negSound + "," +
							oscillations + "\n";
			
			logFileStream.writeMultiByte ( outputData, File.systemCharset);
		}

		function logEventData (eventType:String, imageName:String, soundName:String):void
		{
			var logTime:int = getTimer() - paradigmStartTime;
			
			if (imageName == null){imageName = "";}
			if (soundName == null){soundName = "";}
			
			logFileEventsStream.writeMultiByte (logTime + "," + eventType + "," + imageName + "," + soundName + "\n", File.systemCharset);	
		}
		
		function exitApp ():void 
		{
			var exitingEvent:Event = new Event(Event.EXITING, false, true);
			NativeApplication.nativeApplication.dispatchEvent(exitingEvent);

			if (!exitingEvent.isDefaultPrevented()) {
			NativeApplication.nativeApplication.exit();
			}
		}
		
	}
}