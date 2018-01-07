using namespace cv;
using namespace std;

struct target{
	Point point;
	int area = 0;
	int dist;
	double hwratio;
};

target botarget;
Mat resized;

Mat calibrateBRGHT(Mat mat2calib){											// CALIBRATE MAT BRIGHTNESS *************************
	float avrgbrght;
	float reg = 1;

	mat2calib = mat2calib * reg;
	//Rect area( 0, 0, 25, 25 );											//copies input image in roi
	//Mat calibarea = mat2calib( area );									//computes mean over roi
	Scalar avrcolor = mean( mat2calib );
	//prints out only .val[0] since image was grayscale
	avrgbrght = round((avrcolor[0] + avrcolor[1] + avrcolor[2])/3);
	if (avrgbrght < 120)
		reg += 0.1;
	else if(avrgbrght > 134)
		reg -= 0.1;
	/*else
		cout << "IMG brightness calibrated."<< endl;
	cout << avrgbrght << endl;*/
	return mat2calib;
}
int getangle(Point pt1,Point pt2,Point pt3){								// ANGLE BETWEEN THREE POINTS******************
	Point ab = { pt2.x - pt1.x, pt2.y - pt1.y };
    Point cb = { pt2.x - pt3.x, pt2.y - pt3.y };

    float dot = (ab.x * cb.x + ab.y * cb.y); 								// dot product
   	float cross = (ab.x * cb.y - ab.y * cb.x); 								// cross product yeaah math at work!
    float alpha = atan2(cross, dot);
  	int angle = floor(alpha * 180. / 3.1415 + 0.5);

	if(angle < 0)															// poor man's abs()
		angle = -(angle);
	//cout<<"angle "<<j<<":"<<angle<<"\n";
	return angle;
}

target findfinder(Mat base,bool disp){										//find marker - (mat to process , display finder contours)
	target finder;
	const double epsylon4PolyDP = 4.9;
	const double whratiotolerance = 30;
	const int angtolerance = 10;
	int polyarea = 0;
	double hwratio = 0;
	//double dist = 0;
	double besttarget;
	int angle = 0, ang90 = 0;
	RotatedRect minRect;
	Rect boundRect;

	vector< vector<Point> > contours; 										// raw contours from base
	vector<Vec4i> hierarchy;

	//GaussianBlur( base, base, Size(3,3), 0, 0 );
	inRange(base, Scalar(128, 128, 128), Scalar(255, 255, 255), base);
	imshow("base",base);
    findContours( base, contours, hierarchy,CV_RETR_TREE, CV_CHAIN_APPROX_SIMPLE );	//complete family tree of contours RETR_TREE

	vector< vector<Point> > workvector( contours.size() );
	vector< vector<Point> > workvector2( contours.size() );

	for( int i = 0; i< contours.size();i++){	
		convexHull( Mat(contours[i]), workvector[i], false );
    	approxPolyDP( workvector[i], workvector[i], epsylon4PolyDP, true);
		if (hierarchy[i][2] > -1){
			if (workvector[i].size() < 6 && workvector[i].size() > 3){
				polyarea = contourArea(workvector[i],false);
				if (polyarea > 80 && polyarea < 10000){
					for(int j= 0; j < workvector[i].size();j++){
						int angle = getangle(workvector[i][j],workvector[i][j+1],workvector[i][j+2]);
						if(angle > (90 - angtolerance) && angle < (90 + angtolerance))
							ang90 ++;
						}
						if(ang90 >= 3){
							minRect = minAreaRect( Mat(workvector[i]) );
							hwratio = abs(minRect.size.width - minRect.size.height);
							if ( hwratio < whratiotolerance){
								/*if(disp)
									drawContours( resized, workvector, i, Scalar( 0, 0, 255 ), 2, 1, hierarchy, 0, Point() );*/
								convexHull( Mat(contours[hierarchy[i][2]]), workvector2[i], false );
    							approxPolyDP( workvector2[i], workvector2[i], epsylon4PolyDP, true);						
								if(workvector2[i].size() < 4){
									if (contourArea(workvector2[i],false) > (polyarea/10)){
										if(disp){
											drawContours( resized, contours, hierarchy[i][2], Scalar( 0, 255, 0 ), 2, 3, hierarchy, 0, Point() );
											//drawContours( resized, workvector, i, Scalar( 0, 255, 0 ), 2, 8, hierarchy, 0, Point() ); 
										}
										if (polyarea > finder.area){
											finder.area = polyarea;

											finder.area = polyarea;
											finder.point = minRect.center;
											finder.dist =  ((1 / (((sqrt (polyarea)) * (750/27.4772))*2)) * 1000000)+100;
											finder.hwratio = hwratio;
											//cout<<hwratio<<"\n";
										}
										if(finder.area > 4500){}			//try to read data
											//return finder;
									}
								}
							}
						}
					}
			}
		}	
	}
	return finder;
}


