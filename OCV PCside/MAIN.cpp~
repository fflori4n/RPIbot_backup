//NONAME CONTROL follow finder
#include "opencv2/opencv.hpp"
#include <cmath> 

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <string>
#include <iostream>
#include <signal.h>															// for watchdog

#include "CVfunctions.h"													//My functions in CVfunctions.h 

using namespace cv;
using namespace std;

Mat frame;

float streamtmout = 1;
int speed = 6060;
int randno = 1000;						
bool disp = true;
int i = 0;

Point lasttargpoint = cvPoint(0,0);
int targlost;
int skipproc = 0;
bool targlocked = false;

string OK= "\e[92m[ OK ]\e[39m",ER="\e[93m[ ER ]\e[39m";
string motorval = "0000";
string prevmotorval = "0000";

vector<Point> points;														//for error point correction in processpath

int tcpsoc;																	//vars for tcp
struct sockaddr_in serv_addr;
struct hostent *server;

//************************************************************************** MANAGE TCP SOC. && SEND DATA **************************************
int sendviaTCP(string base, bool init,int repeat = 1){
	fd_set wbuff;
	struct timeval tv;
	tv.tv_sec = 2;
	tv.tv_usec = 0;
	string OK= "\e[92m[ OK ]\e[39m",ER="\e[93m[ ER ]\e[39m";
	string msg="",ledZ= "";
	char host[] = "192.168.12.1";
	char frame[256];
	char buffer[256];
	unsigned int bufsize;
	int tmout = 0,portno = 8234,randno = 1234,lp = 0,Er;
	bool ok = false;
	if(init){
		do{
			tmout++;
			if(tmout > 15){
				cout<<"soc.init timeout!" + ER<<endl;
				exit(0);
			}
			sleep(1);
			tcpsoc = socket(AF_INET, SOCK_STREAM, 0);
    		if (tcpsoc < 0) {
				perror("InitEr");
				ok = false;
			}
   			server = gethostbyname(host);
   			bzero((char *) &serv_addr, sizeof(serv_addr));
   			serv_addr.sin_family = AF_INET;
   			bcopy((char *)server->h_addr,(char *)&serv_addr.sin_addr.s_addr,server->h_length);
   			serv_addr.sin_port = htons(portno);
			if (connect(tcpsoc,(const sockaddr*)&serv_addr,sizeof(serv_addr)) < 0){
				perror("InitEr");
				ok = false;
			}
			else
				ok = true;
		}while(!ok);
		cout<<"socket.init completed!" + OK <<endl;
	}
	else{
		while(1){
			FD_ZERO(&wbuff);
			FD_SET(tcpsoc, &wbuff);
			Er = select(tcpsoc + 1, NULL, &wbuff, NULL, &tv);				//chk if out buffer is overflowing
		
			ledZ="";														
			randno = rand()%(9999+ 1) + 0;
			if(to_string(randno).length() < 4)								//add leading zeros - not good solution
			for(int i= 0;i < (4 - to_string(randno).length());i++)
				ledZ = ledZ + "0";
			msg = base + " " + ledZ+ to_string(randno)+ "\n";				//	+ "\n"
			cout<<msg<<endl;
		
			if (Er > 0) {
				strcpy(frame, msg.c_str());									// not pretty but works
				Er = write(tcpsoc,frame,strlen(frame));
				//Er = write(tcpsoc,"hello world",strlen("hello world"));
				if (Er > 0)
					cout<<"Data is flowing !" + OK<<endl;	
				else
					perror("Write socket error:");
					//cout<<Er<<endl;
					cout<<"error sending!" + ER<<endl;
					//sendviaTCP("",true,1);
			}
			else{
				cout<<"write buffer is full  " + ER <<endl;
				if (Er < 0) {
					perror("WriteEr");
					sleep(1);
					return -1;
				}
			}
			lp++;
			if(lp >= repeat)
				break;
		}
	}
	return 0;
	//close(tcpsoc);
}

//************************************************************************** SELECT TARGET AND SET ROUTE *******************************
void processpath(target target,bool targvisible)	{
	Point sum;
	if(target.area == 0 && targvisible)
		return;
	circle(resized,target.point,45,Scalar(255,0,0));
	putText(resized,"EST.DIST:"+ std::to_string(target.dist),cvPoint((target.point.x + 50),target.point.y), FONT_HERSHEY_DUPLEX, 0.3, cvScalar(255,0,0), 1, CV_AA);
	putText(resized,"AREA:" + std::to_string(target.area), cvPoint((target.point.x + 50),(target.point.y + 10)), FONT_HERSHEY_DUPLEX, 0.3, cvScalar(255,0,0), 1, CV_AA);
	if(targvisible)
		points.push_back(target.point);
	else
		points.push_back(lasttargpoint);
	if(points.size() > 5){
		points.erase(points.begin() + 0);
		for( int i = 0; i< points.size();i++){
			if(i < (points.size() - 1) && norm(points[i] - points[i + 1]) > 45){
				//circle(resized,points[i],15,Scalar(0,0,255));				//Aprox targ !OK - red circle
				points.erase(points.begin() + i);
			}
			else if(i < (points.size() - 1) && norm(points[i] - points[i + 1]) > 5){	// && movingtarget
				sum += points[i];
				//cout<<"target is moving!\n";
			}
			else{
				sum += points[i];
				//cout<<"target is static!\n";
				//circle(resized,points[i],15,Scalar(0,255,0));				// Aprox targ OK - green circle
			}
		}
		Point avrgpoint = cvPoint(sum.x / points.size(),sum.y / points.size());
		if(targvisible)
			lasttargpoint = target.point;
		else{
			targlost++;
			if (targlost > 35 && targlocked){								// trim targlost value
				avrgpoint = lasttargpoint;
				targlost = 0;
			}
		}
		circle(resized,avrgpoint,45,Scalar(100,145,255));
		if(target.area > 4500){
			motorval = "0000";
			targlocked = false;
			circle(resized,avrgpoint,45,Scalar(255,255,255));
			cout<<"Targ reached!"<<endl;
			return;
		}																	// PWMR,DIRR,PWML,DIRL
		else if(target.area < 3000 && target.area > 20){
			targlocked = true;
		}
		prevmotorval = motorval;
		if(avrgpoint.x < 105){
			motorval = "1100";
		}else if(avrgpoint.x >= 105 && avrgpoint.x <= 215){
			motorval = "1010";
		}else if(avrgpoint.x > 215){										// 105,215
			motorval = "0011";
		}else
			motorval = "0000";

		if(motorval != prevmotorval && (motorval == "1100" or motorval == "0011")){
			prevmotorval = motorval;
			skipproc = 3;	
			cout<<"wait for img!"<<endl;
		}
	}

	/*if(target.hwratio < 3){
		//cout<<"target is straight\n";
	}
	else{
		//cout<<"target is angled\n";
	}*/
}

void timeout(int sig){														//Callback for stream timeout
	//sendviaTCP("CV\n",false);
	cout<<"Stream timeout!" + ER<<endl;
	motorval = "0000";
	sendviaTCP("CV " + motorval + " " + "0000",false,5);					//SPEED = 0 and motorval reset
	//alarm(streamtmout);													//Not used for now, may cause stack overflow!
}

int main( int argc, char** argv )	//************************************** INIT ***********************************************************
{
	VideoCapture cap;
	if(!cap.open("http://192.168.12.1:8081/?action=stream?dummy=param.mjpg")){			//read stream (dummy=param.mjpg - so OCV knows its mjpg)
		cout<<"Can't open stream...		 " + ER << endl;
		exit(0);
	}
	sendviaTCP("",true);
	/*if(!cap.open(0))
	{
		cout<<"error - Can't get cam img";
        	return 0;
	}*/
	// ********************************************************************* MAIN *******************************************************
	for(;;)
	{
		motorval = "0000";
		signal(SIGALRM,timeout);
		alarm(streamtmout);
		cap >> frame;
		
		if( frame.empty() ) break; 											// end of video stream
																			//imshow("CAM working! :)", frame);
		resize(frame, resized,Size(320, 240));
		resized = calibrateBRGHT(resized);
		if(skipproc < 1){													// skip img processing if not needed
			botarget = findfinder(resized,true);
			if(botarget.area != 0)
				processpath(botarget,true);
			else if(targlocked)
				processpath(botarget,false);
		}else
			skipproc--;
		sendviaTCP("CV " + motorval + " " + to_string(speed),false,1);
		//sendviaTCP("CV\n",false);
		imshow("resized",resized);

		if( waitKey(1) == 27 ) 
			disp = !(disp);
		//if( waitKey(1) == 27 ) break; 									// stop capturing by pressing ESC 
	}
}

