#raw parser by Shuyi Li 3/21/2017
use strict;
use Data::Dumper;
use Math::Trig;
use Time::Local;
use Time::Piece;
use File::Find::Rule;
use Cwd;
use POSIX;

#use Statistics::Basic qw(:all);
#my $filename = $ARGV[0];
#my $outname= $ARGV[1];
#
#
#
#
#
#
our $pcm_out_dir;
our $pcm_sum_dir ;
our $swp_out_dir;
our $swp_sum_dir;
our $swp_raw_dir;
our $specfile;
our $lot_mapping; 
#Effective Width = 422.5, L=10

require 'H:\\Device development\\TSI\\Scripts\\perl\\config.pl';


my $dir= getcwd;
my @inputfilelist = File::Find::Rule
->file()
->name('*.raw')
->in ($dir);

#my @inputfilelist = glob ('*.raw');


#looping through all raw files 
#
#
#
#
#CV: remove sites with any bad Cap 
#Hall, IDVG: IG: remove site 
#
#sort table by temp, lot, wafer, site, device, and VG

my $specs_upper = {
"HALL" => {
	 "IG"=>1E-10,
        },
"CV" => {
	 "CS"=>1E-10,
        },
"TOXINV" => {
	 "CS"=>1E-10,
        },
"IDVG" => {
	 "IG"=>10E-9,
        },
};

my $specs_lower= {
"CV" => {
	 "CS"=>0,
        },
"TOXINV" => {
	 "CS"=>0,
        },
};

my $Vd = 0.050;
my $Vfb = -1.0;
my $epsilon = 8.854e-12;
my $erox = 3.9;

my $online=0;

foreach (@ARGV) { if ($_=~/online/) { $online=1; } }

my $outputdir = "C:\\raw_parser_output\\";
if ($online) { $outputdir = $swp_out_dir; }

print "Your output is stored at $outputdir\n";

if ( -d $outputdir) {} else { mkdir ($outputdir); }
my $filecat;
#generate raw file hash structure by lot and algo
#
#
#
#
#
#
#
#
#
#pre parse all the input file get all the retest and test plan name out of the raw file
#
my $dupfilehash;
my $filetestplan;




foreach  my $thisinputfile (@inputfilelist)
{
	my @filetmp = split (/\//, $thisinputfile);
	my $shortname =$filetmp[-1];
	my @filesplit = split (/_/, $shortname);
	my $lot=$filesplit[0];
	my $algo;
	if ($shortname=~ /_HALL_/)
	{
		$algo = "HALL"; 
	}
	elsif ($shortname=~ /_CGG_/ ||$shortname=~  /_CGC_/)
	{
		$algo = "CV"; 
	}
	elsif ($shortname=~ /_IDVG_/)
	{
		$algo = "IDVG"; 
	}
	elsif ($shortname=~ /_IGVG_/)
	{
		$algo = "IDVG"; 
	}
	elsif ($shortname=~ /_TOXINV_/)
	{
		$algo = "TOXINV"; 
	}
	else
	{
		$algo = "OTHER"; 
	}


	open (my $thisfile, "<", $thisinputfile) or die "Can't open this file $thisinputfile\n";

	my $wafer;
	my $diex;
	my $diey;
	my $startcapture=0;
	my $finaldata;
	my @header;
	my $temp = 25;
	if ($thisinputfile =~ /85C/)
	{
		$temp=85;
	}
	my @otherheader= 
	(
		"TEMP",
		"LOTID",
		"PROCESSID",
		"TESTPLAN",
		"WAFERID",
		"DATE",
		"TIME",
		"DIEX",
		"DIEY",
		"SITE",
		"MODULE",
		"DEVICE",
		"POINTS",
	);


	my $order=0;
	my $commonheader;
	my $startpoint=0;
	my $point=0;
	while (<$thisfile>)
	{
		$_ =~ s/#//g;
		$_ =~ s/^ +//g;
		chop($_);
		my @thisline = split (/[\t ,]+/);
		foreach my $thisheader (@otherheader)
		{
			if ($thisline[0] =~ /$thisheader/i) { $commonheader->{$thisheader}=$thisline[1];} 
		}
		last if (defined $commonheader->{"TESTPLAN"} && defined $commonheader->{"TIME"} && defined $commonheader ->{"DATE"} && defined $commonheader->{"LOTID"} );

	}
	my $thistime = $commonheader->{"DATE"}." ".$commonheader->{"TIME"};
	my $t = Time::Piece -> strptime ($thistime, "%m/%d/%Y %T");

	my $epochtime = $t->epoch;
	# indexed by lot, testplan, algo, short file name and time stamp;
        $filetestplan->{$thisinputfile}->{"shortfile"}	=  $shortname;
        $dupfilehash->{$shortname}->{$epochtime}=$thisinputfile;
        $filetestplan->{$thisinputfile}->{"lot"}= $commonheader->{"LOTID"};
        $filetestplan->{$thisinputfile}->{"algo"}= $algo;
        $filetestplan->{$thisinputfile}->{"testplan"}=$commonheader->{"TESTPLAN"}; 
	

}


my $refile;
foreach my  $thisfullfile (keys %{$filetestplan}) 
{
	 # re-assign to the refile;

         my $lot= $filetestplan->{$thisfullfile}->{"lot"};
         my $algo= $filetestplan->{$thisfullfile}->{"algo"};
	 my $shortname = $filetestplan->{$thisfullfile}->{"shortfile"};
	 my $thisplan = $filetestplan->{$thisfullfile}->{"testplan"};
	 my @allepoch =   keys %{$dupfilehash->{$shortname}};
	 # if there's ducplicated files
	 if (@allepoch > 1)
	 {
		 my $count=0;
		 foreach my $thisepoch  (sort {$a<=>$b} @allepoch ) # take care of duplicate files
		 {
			 my $tmpfile = $dupfilehash->{$shortname}->{$thisepoch};
	                 my $newplan =  $thisplan."_RETEST".$count;
			 print "found dups $newplan with time stamp $thisepoch\n";
	                 $refile->{$lot}->{$newplan}->{$algo}->{$tmpfile}=$shortname;
			 $count++;
		 }
	 }
	 else
	 {
	         $refile->{$lot}->{$thisplan}->{$algo}->{$thisfullfile}= $shortname;
	 }

}
#	open (my $tmpout, ">", $outputdir."//out.tmp") or die "Can't open this file \n";
#print $tmpout Dumper($refile);

#print $tmpout "===============================\n";
#print $tmpout Dumper($dupfilehash);
#close ($tmpout);

#die;
#foreach (@inputfilelist)
#{
#   my @filesplit = split (/_/);
#   my $lot=$filesplit[0];
#   if (/_HALL_/)
#   {
#    push @{$filecat->{$lot}->{"HALL"}}, $_;
#   }
#   elsif (/_CGG_/ || /_CGC_/)
#   {
#    push @{$filecat->{$lot}->{"CV"}}, $_;
#   }
#   elsif (/_IDVG_/)
#   {
#    push @{$filecat->{$lot}->{"IDVG"}}, $_;
#   }
#   elsif (/_TOXINV_/)
#   {
#    push @{$filecat->{$lot}->{"TOXINV"}}, $_;
#   }
#   else
#   {
#    push @{$filecat->{$lot}->{"OHTER"}}, $_;
#   }
#}

#loop through each lots 
foreach my $thislot (keys %{$refile})
{

 	my $ecm = $lot_mapping->{$thislot};	
	print "Working on lot:$thislot and $ecm\n";
	my $lotdir = $outputdir."//".$thislot."_".$ecm;
	if ( -d $lotdir) {} else { mkdir ($lotdir); }

foreach my $thistestplan (keys %{$refile->{$thislot}})
{
	my $testplandir  = $lotdir."//".$thistestplan;
	if ( -d $testplandir) {} else { mkdir ($testplandir); }

	my $finalcvhall;
	my $finalcvhallname= $testplandir."//".$thislot."_cv_hall.csv";
	open (my $finalcvhall_file, ">", $finalcvhallname) or die "Can't open this file $finalcvhallname\n";
	my $finalcvhall_header;
	my $count;
	print "working on test plan $thistestplan\n";

	#loop through each algo
	foreach my $algo (sort keys %{$refile->{$thislot}->{$thistestplan}})
	{
		print "Working on algo:$algo\n";
		my $sumfilename= $testplandir."//".$thislot."_".$algo."_summary.txt";

		my $algodir = $testplandir."//".$algo;
		if ( -d $algodir) {} else { mkdir ($algodir); }
		my $mergedhash;
		my $mergedname= $algodir."//".$thislot."_".$algo."_merged.csv";
		my $splitname= $algodir."//".$thislot."_".$algo."_split.csv";
		open (my $outfilemerg, ">", $mergedname) or die "Can't open this file $mergedname\n";
		open (my $outsum, ">", $sumfilename) or die "Can't open this file $sumfilename\n";
		open (my $outsplit, ">", $splitname) or die "Can't open this file $splitname\n";
		my $roworder;
		my $stats;
		my $statsplan;
		my $mergedcount=0;
		my $sweepcount;
		my $sweepn=0;
		my $throwaway;
		my $startt=undef;
		my $endt =undef;
		foreach my $tmplongname (keys %{$refile->{$thislot}->{$thistestplan}->{$algo}})
		{
		        my $thisinputfile = $refile->{$thislot}->{$thistestplan}->{$algo}->{$tmplongname};
		        $stats->{"RAWFILE"}->{$thisinputfile}++;

			open (my $thisfile, "<", $tmplongname) or die "Can't open this file $thisinputfile\n";
			my $outname = $thisinputfile;
			$outname =~ s/.raw/.csv/g;
			my $outname= $algodir."//".$outname;
			open (my $outfile, ">", $outname) or die "Can't open this file $outname\n";

			my $wafer;
			my $diex;
			my $diey;
			my $lot;
			my $startcapture=0;
			my $finaldata;
			my @header;
			my $temp = 25;
			if ($thisinputfile =~ /85C/)
			{
				$temp=85;
			}


			my @otherheader= 
			(
				"TEMP",
				"LOTID",
				"PROCESSID",
				"TESTPLAN",
				"WAFERID",
				"DATE",
				"TIME",
				"DIEX",
				"DIEY",
				"SITE",
				"MODULE",
				"DEVICE",
				"POINTS",
			);


			my $order=0;
			foreach (@otherheader) { $roworder->{$_}=$order++; }
			my $commonheader;
			my $startpoint=0;
			my $point=0;
			while (<$thisfile>)
			{
				$_ =~ s/#//g;
				$_ =~ s/^ +//g;
				chop($_);
				my @thisline = split (/[\t ,]+/);
#  print ($thisline [0]."\n");
				foreach my $thisheader (@otherheader)
				{
					if ($thisline[0] =~ /$thisheader/i) { $commonheader->{$thisheader}=$thisline[1];} 
				}



				if ($thisline[0] =~ /^VG$/i  || $thisline[0] =~ /^Vbias$/i || $thisline[0] =~/^VH$/i || $thisline[0] =~/^VD$/i ) {
					$startcapture=1; @header=@thisline; 
					if ($header[0] =~/^Vbias$/)
					{
					   $header[0]  = "VG";  #rename the Vbias crap;
					}
					   for (my $i=0; $i<@header; $i++){$header[$i]  = uc($header[$i]); }

					foreach (@header) { $roworder->{$_}=$order++; }
					$sweepn++;  #keep track the sweep count;
					next;
				}
				if ($thisline[0] =~ /^POINT$/i) { $startpoint =1; next; }
				if ($startpoint ==1) { $point =$thisline[0]; $startpoint=0; next;}
				if ($thisline[0] =~ /Ok/i) {$startcapture=0; }

				if ($startcapture)
				{
					my $thisrow;
					#maping row number to sweeping sequence;
					$sweepcount->{$mergedcount}->{$sweepn}=1;
					foreach my $thisheader (@otherheader)
					{
						$thisrow->{$thisheader}=$commonheader->{$thisheader};
					}
					$thisrow->{"SITE"}= "{".$thisrow->{"DIEX"}.":".$thisrow->{"DIEY"}."}";
					$thisrow->{"TEMP"}= $temp;
					$thisrow->{"POINTS"}= $point;

					my $thistime = $thisrow->{"DATE"}." ".$thisrow->{"TIME"};
					my $t = Time::Piece -> strptime ($thistime, "%m/%d/%Y %T");


					my $tmpdevice = devicemod($thisrow->{"DEVICE"});
					my $tpdevicekey = $thisrow->{"TESTPLAN"}."|".$tmpdevice;

					if (!defined $statsplan->{$tpdevicekey}->{"Date"} ->{"start"}){$statsplan->{$tpdevicekey}->{"Date"} ->{"start"} = $t;}
					if (!defined $statsplan->{$tpdevicekey}->{"Date"} ->{"end"}){$statsplan->{$tpdevicekey}->{"Date"} ->{"end"}= $t;}
					if ($statsplan->{$tpdevicekey}->{"Date"} ->{"start"} >= $t) {$statsplan->{$tpdevicekey}->{"Date"} ->{"start"} = $t};
					if ($statsplan->{$tpdevicekey}->{"Date"} ->{"end"} <= $t) {$statsplan->{$tpdevicekey}->{"Date"} ->{"end"} = $t};
					#print $t."\n";
					#
					
					
					$statsplan->{$tpdevicekey}->{"Date"} -> {"testtime"}=($statsplan->{$tpdevicekey}->{"Date"} ->{"end"}-$statsplan->{$tpdevicekey}->{"Date"} ->{"start"})/60/60;
			                $statsplan->{$tpdevicekey}->{"Wafer"}->{$thisrow->{"WAFERID"}}++; 
			                $statsplan->{$tpdevicekey}->{"SITE"}->{$thisrow->{"SITE"}}++;
			                $statsplan->{$tpdevicekey}->{"RAWFILE"}->{$thisinputfile}++;
					 
					
#2/27/2017	13:44:55

					for (my $i=0; $i<@header; $i++)
					{
						$thisrow->{$header[$i]}= $thisline[$i];

						my $thiskey = $header[$i];
						# flag any bad sweep by checking specs 
						if (defined $specs_upper->{$algo}->{$thiskey})
						{
							if ($thisrow->{$thiskey} > $specs_upper->{$algo}->{$thiskey}) { $stats->{"throwout"}->{$sweepn}=1;  $statsplan->{$tpdevicekey}->{"Breach"}->{$thisrow->{"WAFERID"}}->{$thisrow->{"SITE"}}++;}; 
						}                                                                                                                                                                                                                     
						if (defined $specs_lower->{$algo}->{$thiskey})                                                                                                                                                                        
						{                                                                                                                                                                                                                     
							if ($thisrow->{$thiskey} < $specs_lower->{$algo}->{$thiskey}) { $stats->{"throwout"}->{$sweepn}=1; $statsplan->{$tpdevicekey}->{"Breach"}->{$thisrow->{"WAFERID"}}->{$thisrow->{"SITE"}}++;}; 
						}

					}
					push  @{$finaldata}, $thisrow;
					push  @{$mergedhash}, $thisrow;
					$mergedcount++;
				}

			}

#print Dumper ($finaldata);
			my $j=0;
			foreach my $thisrow (@{$finaldata})
			{
				if ($j==0)
				{
					#print out header;
					foreach my $thiskey (sort {$roworder->{$a}<=>$roworder->{$b}} keys  %$thisrow) { print $outfile $thiskey.","; }
					print $outfile "\n";
				} 
				foreach my $thiskey (sort {$roworder->{$a}<=>$roworder->{$b}} keys %$thisrow)
				{
					print $outfile $thisrow->{$thiskey}.",";
				}
				print $outfile "\n";
				$j++; 
			}

			close($thisfile);
			close($outfile);


		}

		my $j=0;
		$stats->{"ALGO"}->{$algo}=1;	
		$stats->{"LOT"}->{$thislot}=1;	
		my $splitheader= { "TEMP,LOTID,WAFERID,DIEX,DIEY,SITE,DEVICE,VG"=>1, };
		my $splithash;
		my $splitdata;
		my $splithashdie;
		my $tempcount=0;
		#looping throught the merged hash array per each algo
		foreach my $thisrow (@{$mergedhash})
		{
			if ($j==0)
			{
				#print out header;
				foreach my $thiskey (sort {$roworder->{$a}<=>$roworder->{$b}} keys  %$thisrow) { print $outfilemerg $thiskey.","; }
				print $outfilemerg "\n";
			} 
			
			
			#splitting the table
			# device format has to be this way: CGC_1P8V_NFET_SQ_400X10
			# only keep 2nd and 3rd field for the device as the key
			my @tmp = split (/_/,$thisrow->{"DEVICE"});
			my $stripdevice = $tmp[1]."_".$tmp[2]."_".$tmp[3];
			#take care of special case where CGG/CGC is at the end
			if ($tmp[-1] =~ /CGG/i || $tmp[-1] =~ /CGC/i)
			{
				if ($tmp[-1] eq $tmp[2])
				{
					$stripdevice = $tmp[0]."_".$tmp[1];
					$thisrow->{"DEVICE"} =  $tmp[2]."_".$tmp[0]."_".$tmp[1];
				}
				else
				{
					$stripdevice = $tmp[0]."_".$tmp[1]."_".$tmp[2];
					$thisrow->{"DEVICE"} =  $tmp[3]."_".$tmp[0]."_".$tmp[1]."_".$tmp[2];
				}
			}
			
			#ring fet only generate 2 fields 
			if ($tmp[3] =~ /HALL/i || $tmp[3] =~ /SQ/i) 
			{
			 $stripdevice = $tmp[1]."_".$tmp[2];
		        }
			
			my $splitkey = $thisrow->{"TEMP"}.",".$thisrow->{"LOTID"}."," . $thisrow->{"WAFERID"}."," . $thisrow->{"DIEX"}."," . $thisrow->{"DIEY"}.",".  $thisrow->{"SITE"}. ",". $stripdevice.",".$thisrow->{"VG"};

			my $diekey= $thisrow->{"TEMP"}.",".$thisrow->{"LOTID"}."," . $thisrow->{"WAFERID"}."," . $thisrow->{"DIEX"}."," . $thisrow->{"DIEY"}.",".  $thisrow->{"SITE"};
			#screeen out the fliers and merged files
			my $skipthisrow=0;
			if (defined $stats->{'throwout'})
			{
				foreach my $throwoutsweep (keys %{$stats->{'throwout'}})
				{
					if (defined $sweepcount->{$j}->{$throwoutsweep})
					{
#						print "skiping this row $j and $throwoutsweep\n"; 
						$skipthisrow=1;
					}
				}
			}
			$j++; 
			if ($skipthisrow)
			{
#				 next;	
			}

			foreach my $thiskey (sort {$roworder->{$a}<=>$roworder->{$b}} keys %$thisrow)
			{
				print $outfilemerg $thisrow->{$thiskey}.",";
			}
			print $outfilemerg "\n";

			# splitting the table and other algo specific stuff 
			my $CGGo;
			my $CGCo;

			if ($algo eq "CV")
			{
				if ($thisrow->{"DEVICE"} =~ /CGG/i && $thisrow->{"DEVICE"} !~ /OPEN/i)
				{
				
					#update the split key with stripped off Device
					$splithash ->{$splitkey}->{"CGG"} = $thisrow ->{"CS"};
					#$splithash ->{$splitkey}->{"DEVICE"} = $1;
					$splitheader-> {"CGG"}=50;
					#$splitheader-> {"DEVICE"}=101;
				}
				if ($thisrow->{"DEVICE"} =~ /CGG/i && $thisrow->{"DEVICE"} =~ /OPEN/i)
				{
				
					#update the split key with stripped off Device
					$splithash ->{$splitkey}->{"CGG_OPEN"} = $thisrow ->{"CS"};
					#$splithash ->{$splitkey}->{"DEVICE"} = $1;
					$splitheader-> {"CGG_OPEN"}=51;
					#$splitheader-> {"DEVICE"}=101;
				}
				if ($thisrow->{"DEVICE"} =~ /CGC/i && $thisrow->{"DEVICE"} !~ /OPEN/i)
				{
					$splithash ->{$splitkey}->{"CGC"} = $thisrow ->{"CS"};
					#$splithash ->{$splitkey}->{"DEVICE"} = $1;
					$splitheader-> {"CGC"}=49;
					#$splitheader-> {"DEVICE"}=101;
				}
				if ($thisrow->{"DEVICE"} =~ /CGC/i && $thisrow->{"DEVICE"} =~ /OPEN/i)
				{
					$splithash ->{$splitkey}->{"CGC_OPEN"} = $thisrow ->{"CS"};
					#$splithash ->{$splitkey}->{"DEVICE"} = $1;
					$splitheader-> {"CGC_OPEN"}=49;
					#$splitheader-> {"DEVICE"}=101;
				}
				if ($thisrow->{"DEVICE"} =~ /1P8V_/i)
				{
					$splithash ->{$splitkey}->{"VDD"} = 1.8;
					$splitheader-> {"VDD"}=51;
				}
				if ($thisrow->{"DEVICE"} =~ /5V_/i)
				{
					$splithash ->{$splitkey}->{"VDD"} = 5;
					$splitheader-> {"VDD"}=51;
				}
				if ($thisrow->{"DEVICE"} =~ /_(\d+)x(\d+)/i)
				{

				         if ($thisrow->{"DEVICE"} =~ /SQ/i)
					 {
				        	$splithash ->{$splitkey}->{"AREA"} = $1*$2*1E-12*1.1;  #ring FET need to increase area by 10%
				         }
					 else
					 {
				        	$splithash ->{$splitkey}->{"AREA"} = $1*$2*1E-12;  #non_ring_fet
					 }
					$splitheader-> {"AREA"}=52;
				}
				if ($thisrow->{"VG"}  == $Vfb)
				{
					$splithashdie->{$diekey}->{"CGCo"} = $splithash ->{$splitkey}->{"CGC"};
				}
				if ($thisrow->{"VG"}  == $splithash ->{$splitkey}->{"VDD"} )
				{
					$splithashdie->{$diekey}->{"CGGo"} = $splithash ->{$splitkey}->{"CGG"} - $splithash ->{$splitkey}->{"CGC"} +$splithashdie->{$diekey}->{"CGCo"};
				}

			}
			if ($algo eq "HALL")
			{
				if ($thisrow->{"DEVICE"} =~ /_R(\d+)/i)
				{
					my $thisdevice = $1;
					my $thisdevice_Id = $1."_ID";
					if (!defined $thisrow->{"RS"} && $thisrow->{"ID"} !=0)
					{
						$thisrow->{"RS"} = $thisrow->{"VMEAS"}/ $thisrow->{"ID"}* pi / log(2);
					}
					$splithash ->{$splitkey}->{$thisdevice} = $thisrow ->{"RS"};
					$splithash ->{$splitkey}->{$thisdevice_Id} = $thisrow ->{"ID"};
					$splithash ->{$splitkey}->{"DEVICE_FULL"} = $thisrow->{"DEVICE"};
					push @{$splitdata->{$splitkey}}, $thisrow ->{"RS"} if (defined $thisrow->{"RS"});
					$splitheader->{$thisdevice}++;
					$splitheader->{$thisdevice_Id}++;
					$splitheader->{"DEVICE_FULL"}++;
				}

			}
			if ($algo eq "IDVG") #generate the new column based on ID
			{
				my $w = undef;
				my $l = undef;
				if ($thisrow->{"DEVICE"} =~ /_([p\d]+)x([p\d]+)/i)
				{
					 
					$l = $1; $w=$2;
					$l =~ s/p/\./i;
					$w =~ s/p/\./i;
				}
				if ($thisrow->{"ID"} != 0 && defined $w && defined $l  )
			         {	
              				$splithash ->{$splitkey}->{"RS"} = 0.05/$thisrow ->{"ID"}*$l/$w;
              				$splithash ->{$splitkey}->{"DEVICE_FULL"} = $thisrow->{"DEVICE"};
			         }
					$splitheader->{"RS"}++;
					$splitheader->{"DEVICE_FULL"}++;

			}
			$tempcount++;
		}


#		print out summary file

		foreach my $testplan (sort keys %{$statsplan})
		{
			
		print $outsum "\n\n================================================================\n";
		print $outsum "Lot ID:    "; map {print $outsum "\t$_"} sort {$a <=> $b} keys %{$stats->{LOT}};
		print $outsum "\nTest Plan|Device:\t$testplan";
		print $outsum "\nStart Time:"; print $outsum "\t" .$statsplan->{$testplan}->{Date}->{start};
		print $outsum "\nEnd Time:"; print $outsum "\t" .$statsplan->{$testplan}->{Date}->{end};
		print $outsum "\nTest time:\t". sprintf ("%.2f", $statsplan->{$testplan}->{Date}->{testtime}). " Hours";
		print $outsum "\nFile Count:". (keys %{$statsplan->{$testplan}->{RAWFILE}});
		print $outsum "\nGroup:"; map {print $outsum "\t$_"} sort {$a <=> $b} keys %{$stats->{ALGO}};
		print $outsum     "\n==============================================================\n";
		print $outsum "Wafer";
	        map {print $outsum "\t$_"} sort keys %{ $statsplan->{$testplan}->{SITE}};
		print $outsum "\tFail";

	        foreach my $thiswafer (sort {$a <=> $b} keys %{$statsplan->{$testplan}->{Wafer}})
		 {
			 
			 if (defined $statsplan->{$testplan}->{Breach}->{$thiswafer})
			 {


				 print $outsum "\n$thiswafer";
				 my $failcount=0;
				 my $totalcount=0;
				 foreach  my $thissite ( sort keys %{ $statsplan->{$testplan}->{SITE}})
				 {
					 if (defined $statsplan->{$testplan}->{Breach}->{$thiswafer}->{$thissite})
					 {
						 print $outsum "\tX";
						 $failcount++;
					 }
					 else
					 {
						 print $outsum "\t.";
					 }
				       $totalcount++;
				 }
				print $outsum "\t$failcount"."/".$totalcount;
			 }
			 else
			 {
				 my $totalcount=0;
				 print $outsum "\n$thiswafer";
				 foreach  my $thissite ( sort keys %{ $statsplan->{$testplan}->{SITE}})
				 {
					print $outsum "\t.";
				       $totalcount++;
				 }
				print $outsum "\t0"."/".$totalcount;
			 
			 }
		    
		 }
		
		}


		#print out VGID split file;
		if ($algo eq "CV")
		{
#				print (Dumper ($splitheader));
			foreach my $thiskey (sort {$splitheader->{$a}<=>$splitheader->{$b}} keys %{$splitheader})
			{
				print $outsplit $thiskey.",";
				$finalcvhall_header->{$thiskey}= $count++ unless (defined $finalcvhall_header->{$thiskey});
			}
			print $outsplit "\n";
			foreach my $thiskey (sort keys %{$splithash})
			{
				print $outsplit $thiskey.",";
				my $i=0;
				foreach my $thisdata (sort {$splitheader->{$a}<=>$splitheader->{$b}} keys %{$splitheader}) #the key needs to be consistent
				{
					if ($i>0)
					{
					print $outsplit $splithash->{$thiskey}->{$thisdata}.",";
					$finalcvhall->{$thiskey}->{$thisdata}=  $splithash->{$thiskey}->{$thisdata};
					}
					$i++;
				}
				print $outsplit "\n";

			}
		}

		#print out Hall split file
		if ($algo eq "HALL")
		{

#				print (Dumper ($splitheader));
			foreach my $thiskey (sort {$splitheader->{$a}<=>$splitheader->{$b}} keys %{$splitheader})
			{
				print $outsplit $thiskey.",";
			}

			print $outsplit "mean,stdev,Rs,Id\n";
			foreach my $thiskey (sort keys %{$splithash})
			{
				print $outsplit $thiskey.",";
				my $i=0;
				my $tmparray=undef;
				my $tmparray_id=undef;
				foreach my $thisdata (sort {$splitheader->{$a}<=>$splitheader->{$b}} keys %{$splitheader})
				{
					if ($i>0)
					{
					print $outsplit $splithash->{$thiskey}->{$thisdata}.",";
					 if ($thisdata =~ /Id/i)
					 { push @{$tmparray_id},   $splithash->{$thiskey}->{$thisdata} ; }
					 else
					 { push @{$tmparray},   $splithash->{$thiskey}->{$thisdata} ; }
					}
					$i++;
				}

				my $thismean="";
				my $thisstddev="";
				my $thismedian="";
				my $Rs="";
				if (defined $tmparray &&  @{$tmparray} > 0)
				{
					$thismean=&average($tmparray);
					$thisstddev= &stdev($tmparray);
					$thismedian = &median(@$tmparray);
					$Rs= $thismedian;
#					if ($thiskey =~/,2.000E/)
#					{
#						print  "$thiskey\n:@{$tmparray}\n";
#						print  Dumper ($splithash->{$thiskey});
#						print "this mean is $thismean\n";
#					}

					if ($thismean !=0)
					{
						if ( $thisstddev/abs($thismean)> 0.4)
						{
							#		$Rs= ""; 
						
						}
					}
				}

				my $Id="";
				my $thismedian="";
				if (defined $tmparray_id &&  @{$tmparray_id} > 0)
				{
					$thismedian = &median(@$tmparray_id);
					$Id= $thismedian;
				}



				$finalcvhall->{$thiskey}->{'Rs'}= $Rs  if (defined $finalcvhall ->{$thiskey}) ;
				$finalcvhall->{$thiskey}->{'ID'}= $Id  if (defined $finalcvhall ->{$thiskey}) ;
				$finalcvhall_header->{'Rs'}= $count++ unless (defined $finalcvhall_header->{'Rs'});
				$finalcvhall_header->{'ID'}= $count++ unless (defined $finalcvhall_header->{'ID'});
				print $outsplit $thismean.",".$thisstddev.",".$Rs.",".$Id."\n";

			}
		}





		#print out Hall split file
		if ($algo eq "IDVG")
		{

#				print (Dumper ($splitheader));
			foreach my $thiskey (sort {$splitheader->{$a}<=>$splitheader->{$b}} keys %{$splitheader})
			{
				print $outsplit $thiskey.",";
			}

				print $outsplit "\n";
			foreach my $thiskey (sort keys %{$splithash})
			{
				print $outsplit $thiskey.",";
				my $i=0;
				foreach my $thisdata (sort {$splitheader->{$a}<=>$splitheader->{$b}} keys %{$splitheader})
				{
					if ($i>0)
					{
					print $outsplit $splithash->{$thiskey}->{$thisdata}.",";
					}
					$i++;
				}
				print $outsplit "\n";
				$finalcvhall->{$thiskey}->{'Rs_IDVG'}=  $splithash->{$thiskey}->{'RS'} if (defined $finalcvhall->{$thiskey});
				$finalcvhall_header->{'Rs_IDVG'}= $count++ unless (defined $finalcvhall_header->{'Rs_IDVG'});

			}
		}





		close($outsplit);
		close($outfilemerg);
		close($outsum);

	}


	#merge  CV and Rs data 
	
	
				foreach my $thiskey (sort {$finalcvhall_header->{$a}<=>$finalcvhall_header->{$b}} keys %{$finalcvhall_header})
				{
					print $finalcvhall_file $thiskey.",";
				}
				print $finalcvhall_file "\n";
				foreach my $thiskey (sort keys %{$finalcvhall})
				{
					print $finalcvhall_file $thiskey.",";
					my $i=0;
					foreach my $thisdata (sort {$finalcvhall_header->{$a}<=>$finalcvhall_header->{$b}} keys %{$finalcvhall_header})
					{
						if ($i>0)
						{
						print $finalcvhall_file $finalcvhall ->{$thiskey}->{$thisdata}.",";
						}
						$i++;
					}
					print $finalcvhall_file "\n";

				}
			close($finalcvhall_file);
		

}
}




sub average{
        my($data) = @_;
        if (not @$data) {
                die("Empty arrayn");
        }
        my $total = 0;
        foreach (@$data) {
                $total += $_;
        }
        my $average = $total / @$data;
        return $average;
}
sub stdev{
        my($data) = @_;
        if(@$data == 1){
                return 0;
        }
        my $average = &average($data);
        my $sqtotal = 0;
        foreach(@$data) {
                $sqtotal += ($average-$_) ** 2;
        }
        my $std = ($sqtotal / (@$data-1)) ** 0.5;
        return $std;
}
sub median {

return   ((sort {$a <=>$b} @_)[int ($#_/2)] + (sort {$a <=>$b} @_)[ceil ($#_/2)])/2;

}

sub parsedate { 
  my($s) = @_;
  my($year, $month, $day, $hour, $minute, $second);

  if($s =~ m{^\s*(\d{1,4})\W*0*(\d{1,2})\W*0*(\d{1,2})\W*0*
                 (\d{0,2})\W*0*(\d{0,2})\W*0*(\d{0,2})}x) {
    $year = $1;  $month = $2;   $day = $3;
    $hour = $4;  $minute = $5;  $second = $6;
    $hour |= 0;  $minute |= 0;  $second |= 0;  # defaults.
    $year = ($year<100 ? ($year<70 ? 2000+$year : 1900+$year) : $year);
    return timelocal($second,$minute,$hour,$day,$month-1,$year);  
  }
  return -1;
}

sub devicemod {
	my($s) = @_;
	my @tmp = split (/_/,$s);
		my $stripdevice = $tmp[1]."_".$tmp[2]."_".$tmp[3];
		if ($tmp[-1] =~ /CGG/i || $tmp[-1] =~ /CGC/i)
		{
			if ($tmp[-1] eq $tmp[2])
			{
				$stripdevice = $tmp[0]."_".$tmp[1];
				#$thisrow->{"DEVICE"} =  $tmp[2]."_".$tmp[0]."_".$tmp[1];
			}
			else
			{
				$stripdevice = $tmp[0]."_".$tmp[1]."_".$tmp[2];
				#$thisrow->{"DEVICE"} =  $tmp[3]."_".$tmp[0]."_".$tmp[1]."_".$tmp[2];
			}
		}


		#ring fet only generate 2 fields 
		if ($tmp[3] =~ /HALL/i || $tmp[3] =~ /SQ/i) 
		{
			$stripdevice = $tmp[1]."_".$tmp[2];
		}

	return $stripdevice;
}

